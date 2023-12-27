import yaml

from wafl.facts import Fact
from wafl.rules import Rule
from wafl.simple_text_processing.deixis import from_user_to_bot


def get_facts_and_rules_from_text(text: str):
    parsed_text_dict = yaml.safe_load(text)
    fact_strings = parsed_text_dict.get("facts", [])
    rules_list = parsed_text_dict.get("rules", {})

    facts = []
    for text in fact_strings:
        facts.append(
            Fact(
                text=from_user_to_bot(text),
            )
        )

    rules = []
    for rule_dict in rules_list:
        rules.append(
            Rule(
                effect=Fact(text=list(rule_dict.keys())[0]),
                causes=[Fact(item) for item in list(rule_dict.values())[0]],
            )
        )

    return {"facts": facts, "rules": rules}
