import asyncio
import json
import joblib
import os

from wafl.connectors.base_llm_connector import BaseLLMConnector
from wafl.extractors.dataclasses import Query
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)


class LLMChitChatAnswerConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = ""
        prompt += f"""
The user and the bot talk.
The bot must end its utterance with <|END|>.
some examples are as follows:        
        
In the dialogue below a user is speaking to a bot:
user: hello
bot: hello<|END|>


In the dialogue below a user is speaking to a bot:
user: you
bot: what?<|END|>


In the dialogue below a user is speaking to a bot:
user: what
bot: what?<|END|>


In the dialogue below a user is speaking to a bot:
user: what is the colour of the sky
bot: I believe it is blue on a good day<|END|>


In the dialogue below a user is speaking to a bot:
user: who was the lead actor in superman (1978)
bot: I believe it was Christopher Reeve<|END|>


In the dialogue below a user is speaking to a bot:
user: what is the color of the sun
The bot remembers: the sun is bright yellow
bot: The sun is bright yellow<|END|>


In the dialogue below a user is speaking to a bot:
user: what is the height of my truck
The bot remembers: The user's truck is 8ft
bot: The user's truck is 8ft<|END|>


In the dialogue below a user is speaking to a bot:
user: My flat is a one bedroom
bot: nice to know<|END|>
user: is my flat a 2 bedroom
bot: no, it is a 1 bedroom<|END|>


In the dialogue below a user is speaking to a bot:
the bot remembers: The user's name is John
user: is my name Jane
bot: no, your name is John<|END|>


In the dialogue below a user is speaking to a bot:
user: My address is 11 Coulton rd
bot: good to know<|END|>
user: what is my address
the bot remembers: the user's name is John
bot: Your address is 11 Coulton rd<|END|>


In the dialogue below a user is speaking to a bot:
{dialogue}
bot:
        """.strip()
        return prompt
