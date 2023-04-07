from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJChitChatAnswerConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = f"""
In the dialogue below a user is speaking to a bot:
bot: I am fine
user: what
bot: I am fine


In the dialogue below a user is speaking to a bot:
user: what is the color of the sun
The bot remembers: the sun is bright yellow
bot: The sun is bright yellow


In the dialogue below a user is speaking to a bot:
user: what is the height of my truck
The bot remembers: the user's truck is 8ft
bot: The user's truck is 8ft


In the dialogue below a user is speaking to a bot:
user: My flat is a one bedroom
bot: nice to know
user: is my flat a 2 bedroom
bot: no, it is a 1 bedroom


In the dialogue below a user is speaking to a bot:
the bot remembers: the user's name is John
user: is my name Jane
bot: no, your name is John


In the dialogue below a user is speaking to a bot:
user: My address is 11 Coulton rd
bot: good to know
user: what is my address
the bot remembers: the user's name is John
bot: Your address is 11 Coulton rd


In the dialogue below a user is speaking to a bot:
{dialogue}
bot:
        """.strip()
        return prompt
