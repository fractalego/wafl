from typing import List

from wafl.data_objects.dataclasses import Query
from wafl.data_objects.rules import Rule


class RuleMaker:
    def __init__(
        self,
        knowledge: "Knowledge",
        config: "BaseConfig",
        interface: "BaseInterface",
        max_num_rules: int,
        max_recursion: int = 3,
    ):
        self._knowledge = knowledge
        self._config = config
        self._interface = interface
        self._max_num_rules = max_num_rules
        if not config.get_value("max_recursion"):
            self._max_indentation = max_recursion
        else:
            self._max_indentation = config.get_value("max_recursion")

    async def create_from_query(self, conversation: "Conversation") -> List[str]:
        rules = await self._get_rules(conversation)
        rules_texts = []
        for rule in rules:
            rules_text = rule.get_string_using_template(
                "- {effect}:\n{clauses}\n" + rule.indent_str
            )
            rules_texts.append(rules_text)
            await self._interface.add_fact(f"The bot remembers the rule:\n{rules_text}")

        return rules_texts

    async def _get_rules(self, conversation: "Conversation") -> List[Rule]:
        utterances = conversation.get_last_speaker_utterances("user", 1)
        rules = await self._knowledge.ask_for_rule_backward(
            Query.create_from_list(utterances), threshold=0.9
        )

        utterances = conversation.get_last_speaker_utterances("user", 2)
        rules.extend(
            await self._knowledge.ask_for_rule_backward(
                Query.create_from_list(utterances), threshold=0.8
            )
        )

        return rules[: self._max_num_rules]
