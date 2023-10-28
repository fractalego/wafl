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

    async def get_answer(self, text: str, dialogue: str, rules_text: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        prompt = f"""
The following is a summary of a conversation. All the elements of the conversation are described briefly:
A user is chatting with a bot. The chat is happening through a web interface. The user is typing the messages and the bot is replying.
{text}
the currently selected city is eltham.

The following are the rules of the conversation. They *must* be followed closely:
- If the user asks you *create* some code, output the code with the triple backticks syntax: ``` CODE HERE ```
- If the user asks for the weather, asks for the place if you don't know it (the user lives in Eltham, london); SELECTED_PLACE becomes the place; output <execute> print_weather("SELECTED_PLACE") </execute>
- If the user wants a pie, ask for a passport. If the user has a passport, write out just "white rabbit", else write out "blue goose".
- If the user wants some math operation output "The result is <execute>PYTHON CODE THAT RETURNS THE RESULT</execute>".

Create a plausible dialogue based on the aforementioned summary and rules. 
Do not repeat yourself. Be friendly but not too servile.
Wrap any code or html you output in the with the markdown syntax for code blocks (i.e. use triple backticks ```).

This is the dialogue:
{dialogue}
bot:
        """.strip()
        return prompt

    #### make it so only 2 rules max are in the prompt at any time (otherwise it gets confused)
