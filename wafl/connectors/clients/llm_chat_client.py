import os
from typing import List

from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.connectors.prompt_template import PromptTemplate, PromptCreator

_path = os.path.dirname(__file__)


class LLMChatClient:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config
        with open(self._config.get_value("prompt_filename")) as f:
            self.prompt_text = f.read()

    async def get_answers(
        self, text: str, dialogue: str, rules_text: List[str]
    ) -> [str]:
        prompt_template = await self._get_answer_prompt_template(text, dialogue, "\n".join(rules_text))
        return await self._connector.generate(prompt_template)

    async def _get_answer_prompt_template(
        self, text: str, dialogue: "Conversation" = None, rules_text: str = None
    ) -> PromptTemplate:
        return PromptCreator.create_from_arguments(
            prompt=self.prompt_text, conversation=dialogue, facts=text, rules=rules_text
        )
