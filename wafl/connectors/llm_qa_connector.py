import asyncio
import os

from wafl.connectors.remote_llm_connector import RemoteLLMConnector
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMQAConnector(RemoteLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            self._knowledge = None
            self._adversarial_knowledge = None

        else:
            self._knowledge = asyncio.run(self._load_knowledge_from_file("qa", _path))
            self._adversarial_knowledge = asyncio.run(
                self._load_knowledge_from_file("qa_adversarial", _path)
            )

    async def _get_answer_prompt(self, text, query, dialogue=None):
        if not self._knowledge:
            self._knowledge = await self._load_knowledge_from_file("qa", _path)

        if not self._adversarial_knowledge:
            self._adversarial_knowledge = await self._load_knowledge_from_file(
                "qa_adversarial", _path
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
