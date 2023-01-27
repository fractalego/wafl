import re

from nltk import pos_tag
from nltk import word_tokenize


def from_user_to_bot(text):
    text = re.sub("I don't", "the user doesn't", text, flags=re.IGNORECASE)
    text = re.sub("I do not", "the user does not", text, flags=re.IGNORECASE)
    text = re.sub("are you", "is this bot", text, flags=re.IGNORECASE)

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

    return_text = " ".join(new_text)
    return_text = return_text.replace(" @ ", "@")
    return_text = return_text.replace("does n't", "does not")
    return_text = return_text.replace("[ ", "[")
    return_text = return_text.replace(" ]", "]")
    return_text = return_text.replace("{ ", "{")
    return_text = return_text.replace(" }", "}")
    return return_text


def from_bot_to_user(text):
    text = re.sub("the user doesn't", "you don't", text, flags=re.IGNORECASE)
    text = re.sub("the user does not", "you do not", text, flags=re.IGNORECASE)
    text = re.sub("the user does", "you do", text, flags=re.IGNORECASE)
    text = re.sub("the user's", "your", text, flags=re.IGNORECASE)
    text = re.sub("does the user", "do you", text, flags=re.IGNORECASE)
    text = re.sub("is the user", "are you", text, flags=re.IGNORECASE)
    text = re.sub("the user is", "you are", text, flags=re.IGNORECASE)
    text = re.sub("the user", "you", text, flags=re.IGNORECASE)
    text = re.sub("this bot is", "I am", text, flags=re.IGNORECASE)
    text = re.sub("the bot is", "I am", text, flags=re.IGNORECASE)
    return text


def from_bot_to_bot(text):
    text = re.sub("I don't", "The bot doesn't", text, flags=re.IGNORECASE)
    text = re.sub("I do not", "The bot does not", text, flags=re.IGNORECASE)
    text = re.sub("I do not", "The bot does not", text, flags=re.IGNORECASE)
    text = re.sub("you do", "uhe user does", text, flags=re.IGNORECASE)
    text = re.sub("your", "the user's", text, flags=re.IGNORECASE)
    text = re.sub("do you", "does the user", text, flags=re.IGNORECASE)
    text = re.sub("are you", "is the user", text, flags=re.IGNORECASE)
    text = re.sub("you are", "the user is", text, flags=re.IGNORECASE)
    text = re.sub("you", "the user", text, flags=re.IGNORECASE)
    return text
