import re


def get_answer_from_text(text):
    _claim_yn = "The claim makes sense:\n"
    pos = text.find(_claim_yn) + len(_claim_yn)
    return text[pos]


def get_text_up_to_question(text):
    _claim_yn = "The claim makes sense:\n"
    return text[: text.find(_claim_yn) + len(_claim_yn)]


def get_function_description(text):
    if "<" not in text:
        return ""

    return re.sub(r".*<(.*)>$", r"\1", text, re.MULTILINE).strip()


def get_code(text):
    return re.sub(r"(.*)<.*>$", r"\1", text, re.MULTILINE).strip()
