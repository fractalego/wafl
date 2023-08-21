import asyncio
import os
import re

from wafl.connectors.bridges.bridge_implementation import load_knowledge_from_file
from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMChitChatAnswerBridge:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            self._knowledge = None

        else:
            self._knowledge = asyncio.run(
                load_knowledge_from_file("dialogues", self._config)
            )

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        if not self._knowledge:
            self._knowledge = await load_knowledge_from_file("dialogues", self._config)

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
