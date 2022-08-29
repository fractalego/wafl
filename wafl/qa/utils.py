import torch


def get_answer_from_text(text):
    _claim_yn = "The claim makes sense:\n"
    pos = text.find(_claim_yn) + len(_claim_yn)
    return text[pos]


def get_text_up_to_question(text):
    _claim_yn = "The claim makes sense:\n"
    return text[: text.find(_claim_yn) + len(_claim_yn)]
