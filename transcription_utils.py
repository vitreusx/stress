# -*- coding: utf-8 -*-
import re

def remove_braces_content(text):
  return re.sub('\[.*?\]', '', text)

vowels_to_latin = {
        'а': 'q',
        'я': 'q',
        'э': 'w',
        'е': 'w',
        'о': 'e',
        'ё': 'e',
        'у': 'r',
        'ю': 'r',
        'ы': 't',
        'и': 'y',
        '#': 'u'
        }
latin_to_vowels = {
        'q': 'а',
        'w': 'э',
        'e': 'о',
        'r': 'у',
        't': 'ы',
        'y': 'и',
        'u': '#',
        ' ': ' '
        }
fricative_nonpalatalized = {'ш', 'ж', 'ц'}

def get_vowel(latin_letter):
  return latin_to_vowels[latin_letter]

def get_latin(cyrillic_vowel):
  return vowels_to_latin[cyrillic_vowel]

def clean_transcription(phrase, change_to_latin=True):
  bare_phrase = remove_braces_content(phrase)
  bare_phrase += ' '  # To handle correctly the last vowel in case it's the last character
  clean_phrase = ''
  last_vowel = None
  last_fricative_nonpalatalized = False
  for a in bare_phrase:
      a = a.lower()
      if last_vowel:
          if a.encode("unicode_escape") != b'\\u0301' and last_vowel != 'ё':
              last_vowel = '#'
          if last_fricative_nonpalatalized and last_vowel == "и":
              last_vowel = 'ы'
          clean_phrase += vowels_to_latin[last_vowel] if change_to_latin else last_vowel
          last_vowel = None
      last_fricative_nonpalatalized = a in fricative_nonpalatalized
      if a in vowels_to_latin.keys():
          last_vowel = a
  return clean_phrase
