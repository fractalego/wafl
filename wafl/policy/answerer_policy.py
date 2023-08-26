from wafl.connectors.remote.remote_llm_answer_policy_connector import (
    RemoteLLMAnswerPolicyConnector,
)


class AnswerPolicy:
    def __init__(self, config, interface, logger=None):
        self._logger = logger

    async def accept(self, result: str):
        return True
