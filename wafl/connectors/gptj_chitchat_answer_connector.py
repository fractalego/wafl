from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJChitChatAnswerConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = "In the dialogue below a user is speaking to a bot:\n\n"
        if dialogue:
            dialogue = dialogue.strip()
            prompt += dialogue + "\n"

        prompt += "user: " + query + "\n"
        prompt += "bot:"
        return prompt
