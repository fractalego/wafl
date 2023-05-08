from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJPromptPredictorConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = (
            f"Complete the following prompt:\n"
            f"{text}"
        )

        return prompt
