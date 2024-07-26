from dataclasses import dataclass
from enum import Enum
from typing import Union


class Sources(Enum):
    TEXT = 1
    RULES = 2


@dataclass
class Fact:
    text: Union[str, dict]
    is_question: bool = False
    variable: str = None
    is_interruption: bool = False
    destination: str = None
    metadata: Union[str, dict] = None
    source: Sources = Sources.RULES

    def toJSON(self):
        return str(self)
