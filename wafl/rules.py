from dataclasses import dataclass
from typing import List


@dataclass
class Rule:
    effect: "Fact"
    causes: List["Fact"]
    _max_indentation = 3
    indent_str = "  "

    def toJSON(self):
        return str(self)

    def get_string_using_template(self, effect_template: str) -> str:
        rule_str = effect_template.replace("{effect}", self.effect.text)
        rule_str = rule_str.replace("{clauses}", self._get_clauses())
        return rule_str

    def __str__(self):
        rule_str = self.effect.text + "\n"
        return rule_str + self._get_clauses()

    def _get_clauses(self) -> str:
        rule_str = ""
        for cause in self.causes:
            try:
                rule_str += self._recursively_add_clauses(cause)

            except TypeError as e:
                print(f"Error in rule:'''\n{rule_str}'''")
                print("Perhaps the YAML file is not well formatted.")
                print()
                raise e

        return rule_str[:-1]

    def _recursively_add_clauses(self, query: str, depth: int = 1) -> str:
        indentation = self.indent_str * depth
        if type(query) == str:
            return f"{indentation}- {query}\n"

        if type(query.text) == str:
            return f"{indentation}- {query.text}\n"

        if depth > self._max_indentation:
            return ""

        clause = list(query.text.keys())[0]
        rules_text = f"{indentation}- {clause}\n"
        for clauses in query.text.values():
            for cause_index, clause in enumerate(clauses):
                rules_text += self._recursively_add_clauses(clause, depth + 1)

        return rules_text
