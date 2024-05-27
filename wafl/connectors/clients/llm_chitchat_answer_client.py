import os
import textwrap
from typing import List

from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.connectors.prompt_template import PromptTemplate

_path = os.path.dirname(__file__)


class LLMChitChatAnswerClient:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config

    async def get_answer(self, text: str, dialogue: str, rules_text: List[str]) -> str:
        prompt = await self._get_answer_prompt(text, dialogue, "\n".join(rules_text))
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(
        self, text: str, dialogue: "Conversation" = None, rules_text: str = None
    ) -> PromptTemplate:
        return PromptTemplate(
            system_prompt=self._get_system_prompt(text, rules_text),
            conversation=dialogue,
        )

    def _get_system_prompt(self, text, rules_text):
        return f"""
A user is chatting with a bot. The chat is happening through a web interface. The user is typing the messages and the bot is replying.        

This is summary of the bot's knowledge: 
{text.strip()}

The rules that *must* be followed are:
{rules_text.strip()}

Create a plausible dialogue based on the aforementioned summary and rules. 
Do not repeat yourself. Be friendly but not too servile.
Follow the rules if present and they apply to the dialogue. Do not improvise if rules are present. 
        """.strip()
