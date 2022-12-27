from dataclasses import dataclass
from typing import List


@dataclass
class Rule:
    effect: "Fact"
    causes: List["Fact"]
    knowledge_name: str = "/"

    def toJSON(self):
        return str(self)
