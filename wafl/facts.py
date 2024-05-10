from dataclasses import dataclass
from typing import Union


@dataclass
class Fact:
    text: Union[str, dict]
    is_question: bool = False
    variable: str = None
    is_interruption: bool = False
    source: str = None
    destination: str = None

    def toJSON(self):
        return str(self)
