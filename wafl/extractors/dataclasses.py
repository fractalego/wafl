from dataclasses import dataclass

from wafl.simple_text_processing.questions import is_question


@dataclass
class Query:
    text: str
    is_question: bool
    variable: str = None

    @staticmethod
    def create_from_text(text):
        return Query(text=text, is_question=is_question(text))


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

    @staticmethod
    def create_true():
        return Answer(text="true")

    @staticmethod
    def create_false():
        return Answer(text="false")

    @staticmethod
    def create_neutral():
        return Answer(text="unknown")

    @staticmethod
    def create_from_text(text):
        return Answer(text=text)


def normalized(text):
    text = text.strip()
    if not text:
        return ""

    if text[-1] == ".":
        text = text[:-1]

    return text.lower()
