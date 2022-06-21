import rnc
from huggingsound import SpeechRecognitionModel, TrainingArguments, ModelArguments, TokenSet
from pathlib import Path
import os
import argparse
from transcription_utils import remove_braces_content, get_vowel, get_latin, clean_transcription

parser = argparse.ArgumentParser()

parser.add_argument('--data_path', default='',
        help='''Path to the folder containing the csv file and the model folder.
        Defaults to empty string '' which might work if data sits in the current working directory.
        If it doesn't work, then you need to specify the path.''')
parser.add_argument('--train_data', default='all_data20.csv',
        help='''Name of the csv file with the training data, needs to be located in the data path.
        Default: "all_data20" - dataset with videos no longer than 20 seconds.''')
parser.add_argument('--eval_data',
        help='Name of the csv file with the evaluation data, needs to be located in the data path. Defaults: None (not using evaluation during training).')
parser.add_argument('--use_model_from_the_web', action='store_true',
        help='If this flag is not used, use --model_folder argument. If the flag is present, use --model_web_location argument.')
parser.add_argument('--model_folder', default='best_model',
        help='Name of the folder containing the model, needs to be located inside the data path folder. Default: "best_model".')
parser.add_argument('--model_web_location', default='facebook/wav2vec2-large-xlsr-53',
        help='''Name of the web location containing the model, either fine-tuned or only pretrained.
        Note that for a fine-tuned model a token set is already defined.
        Default: "facebook/wav2vec2-large-xlsr-53" - a large model trained on 53 languages from the common_voice dataset.''')
parser.add_argument('--output_dir', default='best_model',
        help='The output directory for the model. Could be the same as the --model_folder. Default: "best_model".')
parser.add_argument('--not_overwrite_output_dir', action='store_true',
        help='If this flag is provided, the --output_dir must point to an empty or non-existing directory (note that by default it points to the model folder).')
parser.add_argument('--num_train_epochs', type=int, default=30,
        help='Training will start from the next epoch compared to the one on which it finished previously. Therefore, we need to increase this number each time.')
args = parser.parse_args()

data_path = args.data_path
RNC_PATH = Path(data_path)
train_path = RNC_PATH / args.train_data  # Slash is a syntax of the pathlib library
eval_path = RNC_PATH / args.eval_data if args.eval_data else None
model_folder = args.model_folder
model_name = args.model_web_location if args.use_model_from_the_web else RNC_PATH / args.model_folder
model = SpeechRecognitionModel(model_name)
output_dir = args.output_dir
overwrite_output_dir = not args.not_overwrite_output_dir
num_train_epochs = args.num_train_epochs

train_corpus = rnc.MultimodalCorpus(file=train_path)
eval_corpus = rnc.MultimodalCorpus(file=eval_path) if eval_path else None
train_data = [
    {"path": str(example.filepath), "transcription": clean_transcription(example.txt)} for example in train_corpus.data
]
eval_data = [
    {"path": str(example.filepath), "transcription": clean_transcription(example.txt)} for example in eval_corpus.data
] if eval_corpus else None

training_args = TrainingArguments()
training_args.per_device_train_batch_size = 24  # Value of 24 was recommended by the creator of the huggingsound library.
training_args.num_train_epochs = num_train_epochs  
training_args.overwrite_output_dir = overwrite_output_dir  # If we don't want to keep the less trained model, it's good to just overwrite the current model directory
#training_args.save_strategy = 'epoch'  # Default save strategy is 'steps'. If we use 'epoch' instead, a model checkpoint will be saved in the end of every epoch.
#training_args.save_steps = 100  # Works only if save strategy is 'steps'. Default value is 500.
#training_args.ignore_data_skip = True  # It seems reasonable to use this option when changing the batch_size but somehow when I set it to True, it didn't work.

tokens = ['q', 'w', 'e', 'r', 't', 'y', 'u']
token_set = TokenSet(tokens)

model.finetune(
    output_dir, 
    train_data=train_data, 
    eval_data=eval_data, # the eval_data is optional
    token_set=token_set,  # token_set won't be used if the model is already fine-tuned and therefore has the token set already defined
    training_args=training_args
)

