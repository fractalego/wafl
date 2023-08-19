from wafl.connectors.remote_llm_answer_policy_connector import (
    RemoteLLMAnswerPolicyConnector,
)


class AnswerPolicy:
    def __init__(self, interface, logger=None):
        self._interface = interface
        self._logger = logger
        self._connector = RemoteLLMAnswerPolicyConnector()
        self._max_num_past_utterances = 3

    async def accept(self, result: str):
        return True
