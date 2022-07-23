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