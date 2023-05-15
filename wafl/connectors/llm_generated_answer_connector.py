from wafl.connectors.base_llm_connector import BaseLLMConnector


class LLMGeneratedAnswerConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = (
            f"The user looks for an answer to the question:\n"
            f"Q: {query}\n"
            f"A: I believe"
        )

        return prompt
