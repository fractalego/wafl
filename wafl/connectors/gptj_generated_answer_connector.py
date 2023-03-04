from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJGeneratedAnswerConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = (
            f"The user looks for an answer to the question:\n"
            f"Q: {query}\n"
            f"A: I believe"
        )

        return prompt
