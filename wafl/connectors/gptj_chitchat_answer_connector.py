from wafl.connectors.base_gptj_connector import BaseGPTJConnector


class GPTJChitChatAnswerConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)

    def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = f"""
In the dialogue below a user is speaking to a bot:
user: hello
bot: [small talk] hello


In the dialogue below a user is speaking to a bot:
user: what is the colour of the sky
bot: [improvised] I believe it is blue on a good day


In the dialogue below a user is speaking to a bot:
user: who was the lead actor in superman (1978)
bot: [improvised] I believe it was Christopher Reeve


In the dialogue below a user is speaking to a bot:
user: what is the color of the sun
The bot remembers: the sun is bright yellow
bot: [factual] The sun is bright yellow


In the dialogue below a user is speaking to a bot:
user: what is the height of my truck
The bot remembers: the user's truck is 8ft
bot: [factual] The user's truck is 8ft


In the dialogue below a user is speaking to a bot:
user: My flat is a one bedroom
bot: nice to know
user: is my flat a 2 bedroom
bot: [answer in conversation] no, it is a 1 bedroom


In the dialogue below a user is speaking to a bot:
the bot remembers: the user's name is John
user: is my name Jane
bot: [factual] no, your name is John


In the dialogue below a user is speaking to a bot:
user: My address is 11 Coulton rd
bot: good to know
user: what is my address
the bot remembers: the user's name is John
bot: [answer in conversation] Your address is 11 Coulton rd


In the dialogue below a user is speaking to a bot:
{dialogue}
bot:
        """.strip()
        return prompt
