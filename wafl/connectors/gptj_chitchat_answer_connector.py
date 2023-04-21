import json
import joblib
import os

from wafl.connectors.base_gptj_connector import BaseGPTJConnector
from wafl.extractors.dataclasses import Query
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)


class GPTJChitChatAnswerConnector(BaseGPTJConnector):
    def __init__(self, config=None):
        super().__init__(config)
        if not os.path.exists(os.path.join(_path, "../data/dialogues.knowledge")):
            with open(os.path.join(_path, "../data/dialogues.json")) as file:
                data = json.load(file)
            self._knowledge = SingleFileKnowledge.create_from_list(
                [item["dialogue"] for item in data]
            )
            joblib.dump(
                self._knowledge, os.path.join(_path, "../data/dialogues.knowledge")
            )

        else:
            self._knowledge = joblib.load(
                os.path.join(_path, "../data/dialogues.knowledge")
            )

    def _get_answer_prompt(self, text, query, dialogue=None):
        retrieved_dialogues = self._knowledge.ask_for_facts(
            Query.create_from_text(dialogue), threshold=0.3
        )
        retrieved_dialogues = [item.text for item in retrieved_dialogues]
        prompt = "\n\n\n".join(retrieved_dialogues) + "\n\n\n"
        prompt += f"""
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
