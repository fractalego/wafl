from wafl.connectors.remote_llm_connector import RemoteLLMConnector


class LLMPromptPredictorConnector(RemoteLLMConnector):
    def __init__(self, config):
        super().__init__(config)

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
