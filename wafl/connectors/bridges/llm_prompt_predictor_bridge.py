from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory


class LLMPromptPredictorBridge:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        for _ in range(5):
            text = text.replace("  ", " ")

        prompt = f"""
<task>
Complete the following task and add <|EOS|> at the end: {text}
</task>
<result>
        """.strip()

        return prompt
