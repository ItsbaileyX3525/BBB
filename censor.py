import random
import re
from pathlib import Path

lines = None
words = None
_censor_chars = '@#$%!'
_censor_pool = []

path = Path(__file__).resolve().parent
    
def get_data(paths):
    return f"{path}\\{paths}"


def get_words():
    if not words:
        load_words()
    return words

def get_censor_char():
    global _censor_pool
    if not _censor_pool:
        _censor_pool = list(_censor_chars)
    return _censor_pool.pop(random.randrange(len(_censor_pool)))    

def contains_profanity(input_text):
    return input_text != censor(input_text)

def censor(input_text):
    ret = input_text
    words = get_words()
    for word in words:
        curse_word = re.compile(re.escape(word), re.IGNORECASE)
        cen = "".join(get_censor_char() for i in list(word))
        ret = curse_word.sub(cen, ret)
    return ret    

def load_words(wordlist=None):
    global words
    if not wordlist:
        filename = get_data('wordlist.txt')
        f = open(filename)
        wordlist = f.readlines()
        wordlist = [w.strip() for w in wordlist if w]
    words = wordlist