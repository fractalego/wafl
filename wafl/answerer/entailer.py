import os
import textwrap

from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.connectors.prompt_template import PromptTemplate
from wafl.interface.conversation import Utterance, Conversation

_path = os.path.dirname(__file__)


class Entailer:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config

    async def left_entails_right(self, lhs: str, rhs: str, dialogue) -> str:
        prompt = await self._get_answer_prompt(lhs, rhs, dialogue)
        result = await self._connector.generate(prompt)
        result = self._clean_result(result)
        return result == "yes"

    async def _get_answer_prompt(self, lhs, rhs, dialogue):
        return PromptTemplate(
            system_prompt="",
            conversation=self._get_dialogue_prompt(lhs, rhs, dialogue),
        )

    def _clean_result(self, result):
        result = result.replace("</task>", "")
        result = result.split("\n")[0]
        result = result.strip()
        return result.lower()

    def _get_dialogue_prompt(self, dialogue, lhs, rhs):
        text = f"""
Your task is to determine whether two sentences are similar.
1) {lhs.lower()}
2) {rhs.lower()}
Please answer "yes" if the two sentences are similar or "no" if not: 
        """.strip()
        return Conversation([Utterance(speaker="user", text=text)])
