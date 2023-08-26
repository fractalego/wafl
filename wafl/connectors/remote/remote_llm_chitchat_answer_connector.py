import asyncio
import os
import re

from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class RemoteLLMChitChatAnswerConnector(RemoteLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            self._knowledge = None

        else:
            self._knowledge = asyncio.run(
                self._load_knowledge_from_file("dialogues", _path)
            )

    async def _get_answer_prompt(self, text, query, dialogue=None):
        if not self._knowledge:
            self._knowledge = await self._load_knowledge_from_file("dialogues", _path)

        retrieved_dialogues = await self._knowledge.ask_for_facts(
            Query.create_from_text(dialogue), threshold=0.1
        )
        retrieved_dialogues = "\n\n\n".join(
            [item.text for item in retrieved_dialogues][:3]
        )
        dialogue = re.sub(r"bot:(.*)\n", r"bot: \1<|EOS|>\n", dialogue)
        prompt = f"""
The user and the bot talk.
The bot ends every utterance line with <|EOS|>.
This bot answers are short and to the point. Do not use more than one sentence to reply.
The bot should not repeat itself. Every reply should be different from the previous ones.
some examples are as follows:


{retrieved_dialogues}


In the dialogue below a user is speaking to a bot:
{dialogue}
bot:
        """.strip()
        return prompt
