import asyncio
import csv

import joblib
import os
import re

from wafl.connectors.llm_connector_factory import LLMConnectorFactory
from wafl.extractors.dataclasses import Query
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)


class LLMChitChatAnswerBridge:
    def __init__(self, config):
        self._llm_connector = LLMConnectorFactory.get_connector(config)
        self._config = config

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            self._knowledge = None

        else:
            self._knowledge = asyncio.run(
                self._load_knowledge_from_file("dialogues", _path)
            )

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._llm_connector.generate(prompt)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        if not self._knowledge:
            self._knowledge = await self._load_knowledge_from_file("dialogues", _path)

        retrieved_dialogues = await self._knowledge.ask_for_facts(
            Query.create_from_text(dialogue), threshold=0.1
        )
        retrieved_dialogues = "\n\n\n".join(
            [item.text for item in retrieved_dialogues][:3]
        )
        dialogue = re.sub(r"bot:(.*)\n", r"bot: \1<|EOS|>\n", dialogue)
        prompt = f"""
The user and the bot talk.
The bot ends every utterance line with <|EOS|>.
This bot answers are short and to the point. Do not use more than one sentence to reply.
The bot should not repeat itself. Every reply should be different from the previous ones.
some examples are as follows:


{retrieved_dialogues}


In the dialogue below a user is speaking to a bot:
{dialogue}
bot:
        """.strip()
        return prompt

    async def _load_knowledge_from_file(self, filename, _path=None):
        items_list = []
        with open(os.path.join(_path, f"../data/{filename}.csv")) as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                items_list.append(row[0].strip())

        knowledge = await SingleFileKnowledge.create_from_list(items_list, self._config)
        joblib.dump(knowledge, os.path.join(_path, f"../data/{filename}.knowledge"))
        return knowledge
