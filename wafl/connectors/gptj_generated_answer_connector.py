from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJGeneratedAnswerConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = (
            "The user looks for an answer to the question:\n"
            "Q: {text}\n"
            "A: I believe"
        )

        return prompt
