import asyncio
import os

from wafl.connectors.bridges.bridge_implementation import load_knowledge_from_file
from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMQABridge:
    def __init__(self, config):
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
            self._knowledge = asyncio.run(load_knowledge_from_file("qa", self._config))
            self._adversarial_knowledge = asyncio.run(
                load_knowledge_from_file("qa_adversarial", self._config)
            )

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        return await self._connector.generate(prompt)

    async def _get_answer_prompt(self, text, query, dialogue=None):
        if not self._knowledge:
            self._knowledge = await load_knowledge_from_file("qa", self._config)

        if not self._adversarial_knowledge:
            self._adversarial_knowledge = await load_knowledge_from_file(
                "qa_adversarial", self._config
            )

        text = text.strip()
        text = text.replace("\\'", "'")
        query = query.strip()
        retrieved_items = await self._knowledge.ask_for_facts_with_threshold(
            Query.create_from_text(f"<story>{text}</story> Q:{query}"), threshold=0.0
        )
        retrieved_adversarial_items = (
            await self._adversarial_knowledge.ask_for_facts_with_threshold(
                Query.create_from_text(f"<story>{text}</story> Q:{query}"),
                threshold=0.0,
            )
        )
        all_items_and_scores = sorted(
            retrieved_items[:5] + retrieved_adversarial_items[:5], key=lambda x: x[1]
        )
        prompt = (
            "\n\n\n".join([item[0].text for item in all_items_and_scores]) + "\n\n\n"
        )

        prompt += (
            "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        )
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += "<story> " + text + " </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them:\n"
        if dialogue:
            dialogue = dialogue.strip()
            prompt += dialogue + "\n"

        prompt += "Q: " + query + "\n"
        prompt += "A:"
        return prompt
