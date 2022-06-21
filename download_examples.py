import rnc
from pathlib import Path
import pandas as pd
import re
import os
import cv2

# RNC_PATH = Path("E:\Rzeczy\ML\Semestr2\RussianStress")
RNC_PATH = Path('')
DATA_PATH = RNC_PATH / 'all_data.csv'


def download_samples(word, n_pages, examples_path):
    mult = rnc.MultimodalCorpus(
        query=word,  # {'вода':  {'gramm': {'numerus': 'pl', 'case': 'nom'}}}, <- for such a query text='lexgramm' is needed
        p_count=n_pages,  # Number of pages (by default there are 5 samples per page)
        accent=1,  # Thanks to this argument we get stress annotations
        lang='ru',
        text='lexform',
        file=examples_path
    )
    # It would be good to somehow tackle a situation when the given word is not found in the corpus.
    # Currently in such cases, the program just throws an error.
    mult.DATA_FOLDER = RNC_PATH
    mult.MEDIA_FOLDER = RNC_PATH / 'media'
    mult.request_examples()  # This function fetches the examples from the corpus
    mult.download_all()  # This function downloads the media (.mp4) files to the MEDIA_FOLDER
    mult.dump()  # This function saves the fetched examples in the examples_path file


def merge_clean_and_remove(csv_to_keep, csv_to_remove, remove=True, clean=True,
                           json_to_remove=None, keep_only_one_person=True, one_sample_per_video=True):
    def number_of_persons(text):
        num = text.count('[')
        return num

    def unseen_video(basename, base_df):
        return basename not in base_df['basename'].values

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
        return number_of_persons(row['text']) <= 1 and unseen_video(row['basename'], base_df) and short_video(row['filename'])

    def get_basename(filename):
        return os.path.basename(filename).rsplit('_', 1)[0]

    def remove_braces_content(text):
        return re.sub('\[.*?\]', '', text)

    df_to_keep = pd.read_csv(csv_to_keep, sep='\t')
    df_to_remove = pd.read_csv(csv_to_remove, sep='\t')
    df_to_remove['basename'] = df_to_remove.apply(lambda x: get_basename(x['filename']), axis=1)

    if keep_only_one_person:
        indices_to_keep = df_to_remove.apply(lambda x: True if keep_row(x, df_to_keep) else False, axis=1)
        rows_non_duplicates = df_to_remove.drop_duplicates(subset='basename', inplace=False).index
        # In fact, it's done not wisely. We should rather find duplicates only among the rows of indices from indices_to_keep.
        # Currently, we just get rid of good rows just because the first row with an example from the same video is bad.
        # If we want the downloading processs to be more efficient, we should fix this stupid mistake.
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
    if remove:
        os.remove(csv_to_remove)
    if json_to_remove:
        os.remove(json_to_remove)


WORDS = ['го́ры', 'горы́', 'де́ла', 'дела́', 'о́кна', 'окна́', 'за́мок', 'замо́к', 'го́ловы', 'головы́', 'сто́роны', 'стороны́',
         'ру́ки', 'руки́', 'но́ги', 'ноги́', 'гу́бы', 'губы́', 'аэропорт', 'аэропорту́', 'понять', 'понял', 'поняла',
         'разделить', 'разделил', 'получил', 'получит', 'упала', 'спала', 'было', 'была', 'не́', 'не']

COLUMNS = ['text', 'source', 'ambiguation', 'found wordforms', 'URL', 'media_url', 'filename', 'basename']


def main():
    helper_name = 'helper'
    helper_csv = RNC_PATH / f'{helper_name}.csv'  # Slash is a syntax of the pathlib library
    helper_json = RNC_PATH / f'{helper_name}.json'
    if not os.path.exists(DATA_PATH):
        df = pd.DataFrame(columns=COLUMNS)
        df.to_csv(DATA_PATH, sep='\t')
    for word in WORDS:
        download_samples(word, 8, helper_csv)
        merge_clean_and_remove(DATA_PATH, helper_csv, json_to_remove=helper_json)


if __name__ == '__main__':
    main()
