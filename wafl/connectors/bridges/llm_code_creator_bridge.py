import asyncio
import os

from wafl.connectors.bridges.bridge_implementation import load_knowledge_from_file
from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMCodeCreatorBridge:
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
                load_knowledge_from_file("code_creator", self._config)
            )

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text: str, task: str, function_name: str = None):
        if self._knowledge is None:
            self._knowledge = await load_knowledge_from_file(
                "code_creator", self._config
            )

        function_name = function_name.split("=")[-1]
        retrieved_items = await self._knowledge.ask_for_facts(
            Query.create_from_text(task), threshold=0.0
        )
        retrieved_items = "\n\n\n".join(
            [item.text for item in retrieved_items][::-1][:5]
        )
        prompt = f"""
{retrieved_items}        
        
The code needs to accomplish the following task: {task}

The function with arguments and output needs to be exactly as in the following. Keep the same names and argument number:
{function_name}

Create a python code that returns the user's request. Import within the function the relevant modules:
        """.strip()

        return prompt
