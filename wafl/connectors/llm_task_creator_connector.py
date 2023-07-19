import asyncio
import os

from wafl.connectors.base_llm_connector import BaseLLMConnector
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMTaskCreatorConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)
        self._knowledge = asyncio.run(self._load_knowledge_from_file("task_creator", _path))

    async def _get_answer_prompt(self, text: str, task: str, triggers: str = None):
        retrieved_items = await self._knowledge.ask_for_facts(
            Query.create_from_text(triggers), threshold=0.1
        )
        retrieved_items = "\n\n\n".join([item.text for item in retrieved_items][:3])
        prompt = f""""
{retrieved_items}


The intention of the user is the following: {task}

The system has rules that are triggered by the following sentences
{triggers}

Create a new rule to answer the user. 
The first line is the rule trigger. 
The following lines are the steps to accomplish the task.
These lines cannot contain the trigger (no recursive tasks are allowed).
A Python function can be added with instructions in English within <...>.
Use the least steps:
        """.strip()

        return prompt
