import asyncio
import os

from wafl.connectors.remote_llm_connector import RemoteLLMConnector
from wafl.extractors.dataclasses import Query

_path = os.path.dirname(__file__)


class LLMTaskExtractorConnector(RemoteLLMConnector):
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
            self._knowledge = asyncio.run(
                self._load_knowledge_from_file("task_extractor", _path)
            )
            self._adversarial_knowledge = asyncio.run(
                self._load_knowledge_from_file("task_extractor_adversarial", _path)
            )

    async def _get_answer_prompt(self, text: str, query: str, dialogue: str = None):
        if self._knowledge is None:
            self._knowledge = await self._load_knowledge_from_file(
                "task_extractor", _path
            )

        if self._adversarial_knowledge is None:
            self._adversarial_knowledge = await self._load_knowledge_from_file(
                "task_extractor_adversarial", _path
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
