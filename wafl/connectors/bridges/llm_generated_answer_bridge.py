from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory


class LLMGeneratedAnswerBridge:
    def __init__(self, config=None):
        self._connector = LLMConnectorFactory.get_connector(config)

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = (
            f"The user looks for an answer to the question:\n"
            f"Q: {query}\n"
            f"A: I believe"
        )

        return prompt
