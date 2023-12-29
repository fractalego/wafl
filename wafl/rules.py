from dataclasses import dataclass
from typing import List


@dataclass
class Rule:
    effect: "Fact"
    causes: List["Fact"]

    def toJSON(self):
        return str(self)

    def __str__(self):
        rule_str = self.effect.text
        for cause in self.causes:
            try:
                rule_str += "\n  " + cause.text

            except TypeError as e:
                print(f"Error in rule:'''\n{rule_str}'''")
                print("Perhaps the YAML file is not well formatted.")
                print()
                raise e

        return rule_str
