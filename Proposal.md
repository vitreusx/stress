# Project Proposal

**Project**: Detecting lexical stress for Russian language (and possibly other Slavic languages)

**Motivation**: In many Slavic languages, like Russian, Ukrainian, Serbo-Croatian and likely others, the position of the word stress isn't as predictable as in Polish. Moreover, there are many pairs of words that have distinct meanings but differ only in the position of the stress. Thus, a model capable of predicting the position of the stress could be useful for understanding the meaning of sentences. Also, word embeddings created by such a stress-aware model would potentially be more appropriate than the currently used models, and could be used on their own to improve e.g. voice synthesizers. Another possible application would be in assisting learners of these languages, as the matter of proper placement of stress is usually difficult for non-native speakers, and we could use a model for detecting stress in annotating texts with stress markers or correcting the mistakes performed by the learner.

**Rough plan**:

- Take a dataset of audio and textual data, preferably one in which the stressed syllables are already provided. Such a corpus is available at e.g. https://ruscorpora.ru/new/en/index.html as a subcorpus `multimodal.` We are in the process of obtaining said subcorpus.) If unsuccessful, we will use `common_voice` dataset (https://huggingface.co/datasets/common_voice/viewer/ru/train) and use tools like an accentizer (https://morpher.ru/accentizer/) or a dictionary with stress annotations (http://speakrus.ru/dict2/index.htm#morph-paradigm).
- Take a pretrained speech recognition model, like wav2vec. We found a version of said model finetuned for Russian (https://huggingface.co/jonatasgrosman/wav2vec2-large-xlsr-53-russian)
- Finetune the model on audio data with stress annotations.

**Prior work**:

- We found some works dealing with lexical stress in English, Dutch or Arabic (for example, https://www.sciencedirect.com/science/article/abs/pii/S0167639315300637), but no such works for Slavic languages.
