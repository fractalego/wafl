from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJChitChatAnswerConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = """
In the dialogue below a user is speaking to a bot:
bot: I am fine
user: what
bot: I am fine
        """.strip()
        prompt += "\n\nIn the dialogue below a user is speaking to a bot:\n"
        if dialogue:
            dialogue = dialogue.strip()
            prompt += dialogue + "\n"

        else:
            prompt += "user: " + query + "\n"

        prompt += "bot:"
        return prompt
