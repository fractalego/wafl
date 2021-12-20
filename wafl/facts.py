from dataclasses import dataclass

@dataclass
class Fact:
    text: str
    is_question: bool = False
    variable: str = None

    def toJSON(self):
        return str(self)
