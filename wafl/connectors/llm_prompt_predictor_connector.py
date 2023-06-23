from wafl.connectors.base_llm_connector import BaseLLMConnector


class LLMPromptPredictorConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        for _ in range(5):
            text = text.replace("  ", " ")

        prompt = f"""
Complete the following prompt and add <|EOS|> at the end:
Add 'a' to the list ["b", "c"]: ["b", "c", "a"]<|EOS|>

Complete the following prompt and add <|EOS|> at the end:
Given the context "the sky is red" answer the following Q: is the sky blue A: no<|EOS|>

Complete the following prompt and add <|EOS|> at the end:
{text}        
        
        """.strip()

        return prompt
