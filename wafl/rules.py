from dataclasses import dataclass
from typing import List


@dataclass
class Rule:
    effect: "Fact"
    causes: List["Fact"]
    knowledge_name: str = "/"

    def toJSON(self):
        return str(self)

    def __str__(self):
        rule_str = self.effect.text
        for cause in self.causes:
            rule_str += "\n  " + cause.text

        return rule_str
