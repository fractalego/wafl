import asyncio
import os

from wafl.connectors.base_llm_connector import BaseLLMConnector
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMQAConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)
        self._knowledge = asyncio.run(self._load_knowledge_from_file("qa", _path))

    async def _get_answer_prompt(self, text, query, dialogue=None):
        text = text.strip()
        text = text.replace("\\'", "'")
        query = query.strip()
        retrieved_items = await self._knowledge.ask_for_facts(
            Query.create_from_text(f"<story>{text}</story> Q:{query}"), threshold=0.1
        )
        retrieved_items = "\n\n\n".join([item.text for item in retrieved_items][:5])
        prompt = retrieved_items + "\n\n\n"

        prompt += (
            "Below a user and a bot discuss a story. The user is talking to the bot.\n"
        )
        prompt += "If the answer is *not* in the story the answer is 'unknown'.\n\n"
        prompt += "<story> " + text + " </story>\n\n"
        prompt += "The first person asks questions about the story and the second answers them. End the answer with <|EOS|>.:\n"
        if dialogue:
            dialogue = dialogue.strip()
            prompt += dialogue + "\n"

        prompt += "Q: " + query + "\n"
        prompt += "A:"
        return prompt
