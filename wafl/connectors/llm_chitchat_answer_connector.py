import asyncio
import os
import re

from wafl.connectors.base_llm_connector import BaseLLMConnector
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMChitChatAnswerConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)
        asyncio.run(self._load_knowledge_from_file("dialogues", _path))

    async def _get_answer_prompt(self, text, query, dialogue=None):
        retrieved_dialogues = await self._knowledge.ask_for_facts(
            Query.create_from_text(dialogue), threshold=0.1
        )
        retrieved_dialogues = "\n\n\n".join([item.text for item in retrieved_dialogues][:3])
        dialogue = re.sub(r"bot:(.*)\n", r"bot: \1<|EOS|>\n", dialogue)
        prompt = f"""
The user and the bot talk.
The bot ends every utterance line with <|EOS|>.
some examples are as follows:


{retrieved_dialogues}


In the dialogue below a user is speaking to a bot:
{dialogue}
bot:
        """.strip()
        return prompt