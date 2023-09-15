import asyncio
import os
import re

from wafl.connectors.bridges.bridge_implementation import load_knowledge_from_file
from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class AnswerFilterBridge:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        dialogue = re.sub(r"bot:(.*)\n", r"bot: \1<|EOS|>\n", dialogue)
        prompt = f"""
The user and the bot talk.
The bot ends every utterance line with <|EOS|>.
This bot answers are short and to the point. Do not use more than one sentence to reply.
The bot should not repeat itself. Every reply should be different from the previous ones.

This is the transcript of their dialogue:
{dialogue}

The bot's intention is to say:
bot: {query}<|EOS|>
 
Refer to "the user" in second person.
Refer to "the bot" in first person.
Do not add any information that is not in the bot's intention. Just rephrase it.
Write the best reply consistent with the bot's intention, in the context of the dialogue above:
bot: 
        """.strip()
        return prompt
