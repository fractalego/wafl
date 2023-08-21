import asyncio
import os

from wafl.connectors.bridges.bridge_implementation import load_knowledge_from_file
from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMTaskExtractorBridge:
    def __init__(self, config=None):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            self._knowledge = None
            self._adversarial_knowledge = None

        else:
            self._knowledge = asyncio.run(
                load_knowledge_from_file("task_extractor", self._config)
            )
            self._adversarial_knowledge = asyncio.run(
                load_knowledge_from_file("task_extractor_adversarial", self._config)
            )

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text: str, query: str, dialogue: str = None):
        if self._knowledge is None:
            self._knowledge = await load_knowledge_from_file(
                "task_extractor", self._config
            )

        if self._adversarial_knowledge is None:
            self._adversarial_knowledge = await load_knowledge_from_file(
                "task_extractor_adversarial", self._config
            )

        retrieved_items = await self._knowledge.ask_for_facts_with_threshold(
            Query.create_from_text(dialogue), threshold=0.0
        )
        retrieved_adversarial_items = (
            await self._adversarial_knowledge.ask_for_facts_with_threshold(
                Query.create_from_text(dialogue), threshold=0.0
            )
        )
        all_items_and_scores = sorted(
            retrieved_items[:5] + retrieved_adversarial_items[:5], key=lambda x: x[1]
        )
        retrieved_string = (
            "\n\n\n".join([item[0].text for item in all_items_and_scores]) + "\n\n\n"
        )

        prompt = f"""
The task is to extract the user's intention from the last statement from the user.
Prior statements only provide context and should not be used to determine the user's intention.
Be as specific as possible.
If the last statement has multiple intentions, separate them with a pipe character "|".
After the task is extracted, end the text with <|EOS|>.
Some examples are below.


{retrieved_string}


The following conversation is taking place:
{dialogue}

Say the user's intention in the last utterance: 
        """.strip()

        return prompt
