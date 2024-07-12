import os
from typing import List

from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.connectors.prompt_template import PromptTemplate

_path = os.path.dirname(__file__)


class LLMChatClient:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config
        with open(self._config.get_value("prompt_filename")) as f:
            self.prompt = f.read()

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
        return (
            self.prompt.replace("{facts}", text.strip())
            .replace("{rules}", rules_text.strip())
            .strip()
        )
