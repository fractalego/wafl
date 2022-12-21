from dataclasses import dataclass


@dataclass
class Query:
    text: str
    is_question: bool
    variable: str = None


@dataclass
class Answer:
    text: str
    variable: str = None

    def is_true(self) -> bool:
        return normalized(self.text) in ["yes", "true"]

    def is_false(self) -> bool:
        return normalized(self.text) in ["no", "false"]

    def is_neutral(self) -> bool:
        return normalized(self.text) in ["unknown"]


def normalized(text):
    text = text.strip()
    if not text:
        return ""

    if text[-1] == ".":
        text = text[:-1]

    return text.lower()
