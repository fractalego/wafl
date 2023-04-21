from wafl.connectors.gptj_answer_policy_connector import GPTJAnswerPolicyConnector


class AnswerPolicy:
    def __init__(self, interface, logger=None):
        self._interface = interface
        self._logger = logger
        self._connector = GPTJAnswerPolicyConnector()

    async def accept(self, result: str):
        text = ""
        dialogue = self._interface.get_utterances_list_with_timestamp()
        choices = self._interface.get_choices_and_timestamp()
        facts = self._interface.get_facts_and_timestamp()
        dialogue_items = dialogue + choices + facts
        dialogue_items = sorted(dialogue_items, key=lambda x: x[0])
        dialogue_items = [item[1] for item in dialogue_items]
        dialogue_items = "\n".join(dialogue_items)
        answer_text = await self._connector.get_answer(text, dialogue_items, result)
        if answer_text.strip()[0].lower() == "y":
            return True

        return False
