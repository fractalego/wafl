class RuleMaker:
    def __init__(
        self,
        knowledge: "Knowledge",
        config: "BaseConfig",
        interface: "BaseInterface",
        max_num_rules: int,
        delete_current_rule: str,
        max_recursion: int = 3,
    ):
        self._knowledge = knowledge
        self._config = config
        self._interface = interface
        self._max_num_rules = max_num_rules
        self._delete_current_rule = delete_current_rule
        if not config.get_value("max_recursion"):
            self._max_indentation = max_recursion
        else:
            self._max_indentation = config.get_value("max_recursion")

    async def create_from_query(self, query):
        rules = await self._knowledge.ask_for_rule_backward(query, threshold=0.92)
        rules = rules[: self._max_num_rules]
        rules_texts = []
        for rule in rules:
            rules_text = rule.get_string_using_template(
                "- If {effect} go through the following points:"
            )
            rules_text += f'{rule.indent_str}- After you completed all the steps output "{self._delete_current_rule}" and continue the conversation.\n'

            rules_texts.append(rules_text)
            await self._interface.add_fact(f"The bot remembers the rule:\n{rules_text}")

        return "\n".join(rules_texts)
