class RuleCreator:
    def __init__(
        self,
        knowledge,
        config,
        interface,
        max_num_rules,
        delete_current_rule,
        max_recursion=1,
    ):
        self._knowledge = knowledge
        self._config = config
        self._interface = interface
        self._max_num_rules = max_num_rules
        self._delete_current_rule = delete_current_rule
        self._max_indentation = max_recursion
        self._indent_str = "    "

    async def create_from_query(self, query):
        rules = await self._knowledge.ask_for_rule_backward(query)
        rules = rules[: self._max_num_rules]
        rules_texts = []
        for rule in rules:
            rules_text = f"- If {rule.effect.text} go through the following points:\n"
            for cause_index, cause in enumerate(rule.causes):
                rules_text += f"{self._indent_str}{cause_index + 1}) {cause.text}\n"
                rules_text += await self.recursively_add_rules(cause)

            rules_text += f'{self._indent_str}{len(rule.causes) + 1}) After you completed all the steps output "{self._delete_current_rule}" and continue the conversation.\n'

            rules_texts.append(rules_text)
            await self._interface.add_fact(f"The bot remembers the rule:\n{rules_text}")

        return "\n".join(rules_texts)

    async def recursively_add_rules(self, query, depth=2):
        rules = await self._knowledge.ask_for_rule_backward(query, threshold=0.95)
        rules = rules[: self._max_num_rules]
        rules_texts = []
        for rule in rules:
            rules_text = f"- If {rule.effect.text} go through the following points:\n"
            for cause_index, causes in enumerate(rule.causes):
                indentation = self._indent_str * depth
                rules_text += f"{indentation}{cause_index + 1}) {causes.text}\n"
                rules_text += await self.recursively_add_rules(causes.text, depth + 1)

            rules_texts.append(rules_text)

        return "\n".join(rules_texts)
