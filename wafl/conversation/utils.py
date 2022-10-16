import re

from nltk import pos_tag
from nltk import word_tokenize

from wafl.conversation.working_memory import WorkingMemory
from wafl.inference.utils import normalized
from wafl.qa.dataclasses import Query


def is_question(text):
    text = text.strip()
    if not text:
        return False

    if text[-1] == "?":
        return True

    if ", the user says" in text:
        return False

    text = re.sub("^Are", "are", text)
    text = re.sub("^Am", "am", text)

    word_and_pos_list = pos_tag(word_tokenize(text))
    first_tag = word_and_pos_list[0][1]
    if first_tag in ["VBZ", "VBD", "VBP", "MD", "WRB", "WP", "WDT"]:
        return True

    return False


def is_yes_no_question(text):
    text = text.strip()
    if not text:
        return False

    text = re.sub("^Are", "are", text)
    text = re.sub("^Am", "am", text)

    word_and_pos_list = pos_tag(word_tokenize(text))
    first_tag = word_and_pos_list[0][1]
    if first_tag in ["VBZ", "VBD", "VBP", "MD"]:
        return True

    return False


def get_sentence_from_yn_question(text):
    text = text.strip()
    text = text.replace("?", "")
    if not text:
        return ""

    triggers_list = [
        ("NN", "DT"),
        ("NNP", "DT"),
        ("NN", "JJ"),
        ("NNP", "JJ"),
        ("NN", "RB"),
        ("NNP", "RB"),
        ("NN", "VBG"),
        ("NNP", "VBG"),
        ("NN", "VB"),
        ("NN", "VBP"),
        ("NN", "VBD"),
        ("NNP", "VB"),
        ("NNP", "VBP"),
        ("NN", "VBN"),
        ("NNP", "VBN"),
        ("NNP", "VBD"),
        ("NNS", "DT"),
        ("NNS", "JJ"),
        ("NNS", "RB"),
        ("NNS", "VBG"),
        ("NNS", "VBN"),
        ("NNS", "VBD"),
        ("NNS", "VB"),
        ("NNS", "VBP"),
        ("PRP", "DT"),
        ("PRP", "JJ"),
        ("PRP", "RB"),
        ("PRP", "VBG"),
        ("PRP", "VBN"),
        ("PRP", "VBD"),
        ("PRP", "VB"),
        ("PRP", "VBP"),
    ]

    word_and_pos_list = pos_tag(word_tokenize(text))
    first_word = word_and_pos_list[0][0].lower()
    new_word_list = []
    words_has_been_added = False
    for index in range(1, len(word_and_pos_list[1:])):
        new_word_list.append(word_and_pos_list[index][0])
        curr_pos = word_and_pos_list[index][1]
        next_pos = word_and_pos_list[index + 1][1]
        if not words_has_been_added and (curr_pos, next_pos) in triggers_list:
            new_word_list.append(first_word)
            words_has_been_added = True

    if not words_has_been_added:
        new_word_list.append(first_word)

    new_word_list.append(word_and_pos_list[-1][0])
    return " ".join(new_word_list)


def get_answer_using_text(inference, interface, text):
    working_memory = WorkingMemory()
    text = text.capitalize()
    if not is_question(text):
        query_text = f"The user says: '{text}.'"
        working_memory.add_story(query_text)

    else:
        query_text = text

    query = Query(text=query_text, is_question=is_question(text), variable="name")
    interface.bot_has_spoken(False)
    answer = inference.compute(query, working_memory)

    if query.is_question and answer.text == "False":
        query = Query(
            text=f"The user asks: '{text}.'",
            is_question=is_question(text),
            variable="name",
        )
        working_memory = WorkingMemory()
        working_memory.add_story(query.text)
        interface.bot_has_spoken(False)
        answer = inference.compute(query, working_memory)

    return answer


def input_is_valid(text):
    if not text.strip():
        return False

    if normalized(text) != "no" and len(text) <= 2:
        return False

    return True
