import re

from nltk import pos_tag
from nltk import word_tokenize


def from_user_to_bot(text):
    word_and_pos_list = pos_tag(word_tokenize(text))
    new_text = []
    for word, pos in word_and_pos_list:
        if word.lower() in ["my", "mine"] and pos == "PRP$":
            new_text.append("the user's")

        elif word.lower() in ["your", "yours"] and pos == "PRP$":
            new_text.append("this bot's")

        elif word.lower() in ["i", "me", "myself"] and pos == "PRP":
            new_text.append("the user")

        elif word.lower() in ["you", "yourself"] and pos == "PRP":
            new_text.append("this bot")

        elif word.lower() in ["am"] and pos == "VBP":
            new_text.append("is")

        else:
            new_text.append(word)

    return " ".join(new_text)


def from_bot_to_user(text):
    text = re.sub("the user's", "your", text, flags=re.IGNORECASE)
    text = re.sub("is the user", "are you", text, flags=re.IGNORECASE)
    text = re.sub("does the user", "do you", text, flags=re.IGNORECASE)
    text = re.sub("the user is", "you are", text, flags=re.IGNORECASE)
    text = re.sub("the user", "you", text, flags=re.IGNORECASE)
    return text
