from typing import List

from wafl.connectors.gptj_rule_policy_connector import GPTJRulePolicyConnector
from wafl.rules import Rule


class RulePolicy:
    def __init__(self, interface, logger=None):
        self._interface = interface
        self._logger = logger
        self._connector = GPTJRulePolicyConnector()
        self._max_num_past_utterances = 3

    async def select(self, rules: List[Rule], query: str) -> List[Rule]:
        rules_text = ""
        for index, rule in enumerate(rules):
            rules_text += f"{index + 1}. {rule.effect.text}\n"

        rules_text += f"{len(rules) + 1}. None of the above\n"
        rules_text = rules_text.strip()

        dialogue = self._interface.get_utterances_list_with_timestamp()[-self._max_num_past_utterances :]
        start_time = -1
        if dialogue:
            start_time = dialogue[0][0]

        choices = self._interface.get_choices_and_timestamp()
        facts = self._interface.get_facts_and_timestamp()
        dialogue_items = dialogue + choices + facts
        dialogue_items = sorted(dialogue_items, key=lambda x: x[0])
        dialogue_items = [item[1] for item in dialogue_items if item[0] >= start_time]
        dialogue_items = "\n".join(dialogue_items)
        if not dialogue_items:
            dialogue_items = f"user: {query}"

        answer_text = await self._connector.get_answer("", dialogue_items, rules_text)
        candidates = answer_text.split(",")
        final_candidates = []
        for candidate in candidates:
            if candidate and candidate.isnumeric() and int(candidate) <= len(rules):
                final_candidates.append(rules[int(candidate) - 1])

        return final_candidates
