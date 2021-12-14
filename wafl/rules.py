from dataclasses import dataclass
from typing import List

@dataclass
class Rule:
    effect: str
    causes: List[str]

    def toJSON(self):
        return str(self)


