import asyncio
import os

from wafl.connectors.base_llm_connector import BaseLLMConnector
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMTaskExtractorConnector(BaseLLMConnector):
    def __init__(self, config=None):
        super().__init__(config)
        self._knowledge = asyncio.run(self._load_knowledge_from_file("task_extractor", _path))

    async def _get_answer_prompt(self, text: str, query: str, dialogue: str = None):
        retrieved_items = await self._knowledge.ask_for_facts(
            Query.create_from_text(dialogue), threshold=0.1
        )
        retrieved_items = "\n\n\n".join([item.text for item in retrieved_items][:3])
        prompt = f"""
The task is to extract the user's intention from the last statement from the user.
Prior statements only provide context and should not be used to determine the user's intention.
Be as specific as possible.
If the last statement has multiple intentions, separate them with a pipe character "|".
After the task is extracted, end the text with <|EOS|>.
Some examples are below.


{retrieved_items}


The following conversation is taking place:
{dialogue}

Say the user's intention in the last utterance: 
        """.strip()

        return prompt
