import re

from nltk import pos_tag
from nltk import word_tokenize

from wafl.conversation.working_memory import WorkingMemory
from wafl.inference.utils import normalized
from wafl.qa.qa import Query


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
