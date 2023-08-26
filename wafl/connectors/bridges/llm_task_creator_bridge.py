import asyncio
import os

from wafl.connectors.bridges.bridge_implementation import load_knowledge_from_file
from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMTaskCreatorBridge:
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
                load_knowledge_from_file("task_creator", self._config)
            )

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text: str, task: str, triggers: str = None):
        if self._knowledge is None:
            self._knowledge = await load_knowledge_from_file(
                "task_creator", self._config
            )

        retrieved_items = await self._knowledge.ask_for_facts(
            Query.create_from_text(task), threshold=0.0
        )
        retrieved_items = "\n\n\n".join(
            [item.text for item in retrieved_items][::-1][:5]
        )
        prompt = f"""" + "\n"
{retrieved_items}


The intention of the user is the following: {task}

The system has rules that are triggered by the following sentences
{triggers}

Create a new rule to answer the user. 
The first line is the rule trigger. 
The following lines are the steps to accomplish the task.
These lines cannot contain the trigger (no recursive tasks are allowed).
A Python function can be added with instructions in English within <...>.
The result of a query can be used within another query by using brackets {{...}}.
Use the least steps:
        """.strip()

        return prompt
