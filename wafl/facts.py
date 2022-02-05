from dataclasses import dataclass


@dataclass
class Fact:
    text: str
    is_question: bool = False
    variable: str = None
    is_interruption: bool = False

    def toJSON(self):
        return str(self)
