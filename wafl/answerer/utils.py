import re


def remove_text_between_brackets(text: str) -> str:
    return re.sub(r"(\[.*?\])", "", text)
