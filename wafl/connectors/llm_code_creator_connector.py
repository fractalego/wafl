import asyncio
import os

from wafl.connectors.base_llm_connector import BaseLLMConnector
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMCodeCreatorConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)
        self._knowledge = asyncio.run(self._load_knowledge_from_file("task_creator", _path))

    async def _get_answer_prompt(self, text: str, task: str, function_name: str = None):
        function_name = function_name.split("=")[-1]
        retrieved_items = await self._knowledge.ask_for_facts(
            Query.create_from_text(task), threshold=0.1
        )
        retrieved_items = "\n\n\n".join([item.text for item in retrieved_items][:3])
        prompt = f"""
{retrieved_items}        
        
The code needs to accomplish the following task: {task}

The function with arguments and output needs to be exactly as in the following. Keep the same names and argument number:
{function_name}

Create a python code that returns the user's request. Import within the function the relevant modules:
        """.strip()

        return prompt
