import re

from nltk import pos_tag
from nltk import word_tokenize


def is_question(text):
    text = text.strip()
    if not text:
        return False

    if text[-1] == "?":
        return True

    text = re.sub("^Are", "are", text)
    text = re.sub("^Am", "am", text)

    word_and_pos_list = pos_tag(word_tokenize(text))
    first_tag = word_and_pos_list[0][1]
    if first_tag in ["VBZ", "VBD", "VBP", "MD", "WRB", "WP", "WDT"]:
        return True

    return False
