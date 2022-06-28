import rnc
from pathlib import Path
import pandas as pd
import re
import os
import shutil
import argparse
import cv2

parser = argparse.ArgumentParser()

parser.add_argument('words', nargs='+',
        help='List of the words to query the Russian National Corpus for.')
parser.add_argument('--data_path', default='',
        help='''Path to the directory in which the csv file and the media folder should be created.
        Defaults to empty string '' which might work if data sits in the current working directory.
        If it doesn't work, then you need to specify the path.''')
parser.add_argument('--examples_basename', dest='basename', default='new_data.csv',
        help='Name of the csv file to write data to.')
parser.add_argument('--helper_basename', dest='helper_name', default='helper',
        help='Helper csv file (will be deleted when the program finishes running).')
parser.add_argument('--media_folder', default='media',
        help='Name of the folder to save the video files in.')
parser.add_argument('--pages_per_word', type=int, default=4,
        help='Number of pages per word (each page contains 5 examples).')
args = parser.parse_args()

helper_name = args.helper_name

RNC_PATH = Path(args.data_path)
CSV_FILE = RNC_PATH / args.basename
MEDIA_PATH = RNC_PATH / args.media_folder
WORDS = args.words
pages_per_word = args.pages_per_word


def download_samples(word, n_pages, examples_path):
    mult = rnc.MultimodalCorpus(
        query=word,
        p_count=n_pages,  # Number of pages (by default there are 5 samples per page)
        accent=1,  # Thanks to this argument we get stress annotations
        lang='ru',
        text='lexform',
        file=examples_path
    )
    # It would be good to somehow tackle a situation when the given word is not found in the corpus.
    # Currently in such cases, the program just throws an error.
    mult.DATA_FOLDER = RNC_PATH
    mult.MEDIA_FOLDER = MEDIA_PATH
    mult.request_examples()  # This function fetches the examples from the corpus
    mult.download_all()  # This function downloads the media (.mp4) files to the MEDIA_FOLDER
    mult.dump()  # This function saves the fetched examples in the examples_path file


def merge_clean_and_remove(csv_to_keep, csv_to_remove, remove=True, clean=True, copy_json=False,
                           keep_only_one_person=True, one_sample_per_video=False):
    def number_of_persons(text):
        num = text.count('[')
        return num

    def unseen_video(name, base_df):
        if one_sample_per_video:
            return name not in base_df['basename'].values
        else:
            return name not in base_df['filename'].values

    def short_video(filename, threshold=20):
        data = cv2.VideoCapture('./'+filename)
        frames = data.get(cv2.CAP_PROP_FRAME_COUNT)
        fps = int(data.get(cv2.CAP_PROP_FPS))
        if fps == 0:
            print(f'FPS = 0 in {filename}')
            return False
        seconds = frames / fps
        return seconds < threshold

    def keep_row(row, base_df):
        name = row['basename'] if one_sample_per_video else row['filename']
        return number_of_persons(row['text']) <= 1 and unseen_video(name, base_df) and short_video(row['filename'])

    def get_basename(filename):
        return os.path.basename(filename).rsplit('_', 1)[0]

    def remove_braces_content(text):
        return re.sub('\[.*?\]', '', text)

    df_to_keep = pd.read_csv(csv_to_keep, sep='\t')
    df_to_remove = pd.read_csv(csv_to_remove, sep='\t')
    for df in [df_to_keep, df_to_remove]:
        if 'basename' not in df.columns:
            df['basename'] = df.apply(lambda x: get_basename(x['filename']), axis=1)

    if keep_only_one_person:
        indices_to_keep = df_to_remove.apply(lambda x: True if keep_row(x, df_to_keep) else False, axis=1)
        if one_sample_per_video:
            rows_non_duplicates = df.to_remove[indices_to_keep].drop_duplicates(subset='basename', inplace=False).index
            indices_to_keep = pd.DataFrame(indices_to_keep).apply(lambda x: True if x[0] == True and x.name in rows_non_duplicates else False, axis=1)
        if remove:
            videos_to_remove = df_to_remove.filename[indices_to_keep == False]
            for vtr in videos_to_remove:
                os.remove(vtr)
        df_to_remove = df_to_remove[indices_to_keep]
    df_len = len(df_to_remove.index)
    if clean and df_len > 0:
        df_to_remove['text'] = df_to_remove.apply(lambda x: remove_braces_content(x['text']), axis=1)
    df_to_keep = pd.concat([df_to_keep, df_to_remove], axis=0)
    df_to_keep.to_csv(csv_to_keep, sep='\t', index=False)

    json_to_remove = str(csv_to_remove)[:-3] + 'json'
    if copy_json:
        json_to_keep = str(csv_to_keep)[:-3] + 'json'
        shutil.copyfile(json_to_remove, json_to_keep)    
    if remove:
        os.remove(csv_to_remove)
        os.remove(json_to_remove)


COLUMNS = ['text', 'source', 'ambiguation', 'found wordforms', 'URL', 'media_url', 'filename', 'basename']


def main():
    helper_csv = RNC_PATH / f'{helper_name}.csv'  # Slash is a syntax of the pathlib library
    helper_json = RNC_PATH / f'{helper_name}.json'
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(CSV_FILE, sep='\t', index=False)
    copy_json = True
    for word in WORDS:
        download_samples(word, pages_per_word, helper_csv)
        merge_clean_and_remove(CSV_FILE, helper_csv, copy_json=copy_json)
        copy_json = False
    df = pd.read_csv(CSV_FILE, sep='\t')
    df.drop('basename', axis=1, inplace=True)
    df.to_csv(CSV_FILE, sep='\t', index=False)


if __name__ == '__main__':
    main()
