from wafl.connectors.gptj_answer_policy_connector import GPTJAnswerPolicyConnector


class AnswerPolicy:
    def __init__(self, interface, logger=None):
        self._interface = interface
        self._logger = logger
        self._connector = GPTJAnswerPolicyConnector()

    async def accept(self, result: str):
        text = ""
        dialogue = self._interface.get_utterances_list()
        answer_text = await self._connector.get_answer(text, dialogue, result)
        if answer_text.strip()[0].lower() == "y":
            return True

        return False
