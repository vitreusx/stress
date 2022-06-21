import rnc
from huggingsound import SpeechRecognitionModel
from pathlib import Path
import os
import argparse
from transcription_utils import remove_braces_content, get_vowel, get_latin, clean_transcription

parser = argparse.ArgumentParser()

parser.add_argument('--transcribe_sents', type=int, dest='transcribe', default=1, help='How many sentences to transcribe')
parser.add_argument('--evaluate_sents', type=int, dest='evaluate', default=10, help='On how many sentences to run the evaluation')
parser.add_argument('--data_path', default='', help='''Path to the folder containing the csv file and the model folder.
        Defaults to empty string '' which might work if data sits in the current working directory.
        If it doesn't work, then you need to specify the path.''')
parser.add_argument('--examples_basename', dest='basename', default='all_data20.csv',
        help='Name of the csv file, needs to be located in the data path.')
parser.add_argument('--model_folder', default='best_model',
        help='Name of the folder containing the model, needs to be located inside the data path folder.')
args = parser.parse_args()

transcribe = args.transcribe
evaluate = args.evaluate
data_path = args.data_path
basename = args.basename
model_folder = args.model_folder

RNC_PATH = Path(data_path)
examples_path = RNC_PATH / basename  # Slash is a syntax of the pathlib library
model = SpeechRecognitionModel(RNC_PATH / model_folder)

mult = rnc.MultimodalCorpus(file=examples_path)


audio_paths = []
phrases = []
phrases_vowels = []
for td in mult.data[:transcribe]:
    audio_paths.append(RNC_PATH / td.filepath)
    phrases.append(remove_braces_content(td.txt))
    phrases_vowels.append(clean_transcription(td.txt, change_to_latin=False))

transcriptions = model.transcribe(audio_paths)
cyrillic_transcriptions = [''.join([get_vowel(vowel) for vowel in tr['transcription']]) for tr in transcriptions]
print('\n'.join(['\n'.join([phr, f'Vowels only: {phr_v}', f'Transcribed: {ct}'])
    for phr, phr_v, ct in zip(phrases, phrases_vowels, cyrillic_transcriptions)]) )

train_data = [ {"path": str(RNC_PATH / str(example.filepath)), "transcription": clean_transcription(example.txt)} for example in mult.data[:evaluate] ]

evaluation = model.evaluate(train_data[:evaluate])
print(evaluation)
