from dataclasses import dataclass
from enum import Enum
from typing import Union


class Sources(Enum):
    FROM_TEXT = 1
    FROM_RULES = 2


@dataclass
class Fact:
    text: Union[str, dict]
    is_question: bool = False
    variable: str = None
    is_interruption: bool = False
    destination: str = None
    metadata: Union[str, dict] = None
    source: Sources = Sources.FROM_RULES

    def toJSON(self):
        return str(self)

    def copy(self):
        return Fact(
            self.text,
            self.is_question,
            self.variable,
            self.is_interruption,
            self.destination,
            self.metadata,
            self.source,
        )
