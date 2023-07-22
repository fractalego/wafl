from wafl.connectors.llm_answer_policy_connector import LLMAnswerPolicyConnector


class AnswerPolicy:
    def __init__(self, interface, logger=None):
        self._interface = interface
        self._logger = logger
        self._connector = LLMAnswerPolicyConnector()
        self._max_num_past_utterances = 3
        self.improvise = False

    async def accept(self, result: str):
        return True

    def _get_unique_items(self, dialogue_items):
        unique_dialogue_items = [dialogue_items[0]]
        prior_items = set()
        for index, item in enumerate(dialogue_items[1:]):
            prior_item = dialogue_items[index]
            if item not in prior_item:
                unique_dialogue_items.append(item)

            prior_items.add(item)

        return unique_dialogue_items
