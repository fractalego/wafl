from wafl.connectors.gptj_answer_policy_connector import GPTJAnswerPolicyConnector


class AnswerPolicy:
    def __init__(self, interface, logger=None):
        self._interface = interface
        self._logger = logger
        self._connector = GPTJAnswerPolicyConnector()

    async def accept(self, result: str, task_memory: "TaskMemory" = None):
        text = ""
        dialogue = self._interface.get_utterances_list_with_timestamp()
        if task_memory:
            choices = task_memory.get_choices_and_timestamp()

        else:
            choices = []

        dialogue_and_choices = dialogue + choices
        dialogue_and_choices = sorted(dialogue_and_choices)
        dialogue_and_choices = [item[1] for item in dialogue_and_choices]
        dialogue_and_choices = "\n".join(dialogue_and_choices)
        answer_text = await self._connector.get_answer(
            text, dialogue_and_choices, result
        )
        if answer_text.strip()[0].lower() == "y":
            return True

        return False
