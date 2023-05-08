from wafl.connectors.gptj_answer_policy_connector import GPTJAnswerPolicyConnector


class AnswerPolicy:
    def __init__(self, interface, logger=None):
        self._interface = interface
        self._logger = logger
        self._connector = GPTJAnswerPolicyConnector()

    async def accept(self, result: str):
        text = ""
        dialogue = self._interface.get_utterances_list_with_timestamp()
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
            return True

        answer_text = await self._connector.get_answer(text, dialogue_items, result)
        if answer_text and answer_text.strip()[0].lower() == "y":
            return True

        return False
