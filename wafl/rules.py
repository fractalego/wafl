from dataclasses import dataclass
from typing import List


@dataclass
class Rule:
    effect: "Fact"
    causes: List["Fact"]

    def toJSON(self):
        return str(self)
