import logging
import os

from wafl.connectors.bridges.llm_task_extractor_bridge import LLMTaskExtractorBridge
from wafl.extractors.dataclasses import Answer

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class TaskExtractor:
    def __init__(self, config, interface, logger=None):
        self._interface = interface
        self._connector = LLMTaskExtractorBridge(config)
        self._max_num_past_utterances = 3
        self._to_ignore = ["yes", "no", "ok", "okay", "sure", "nope", "yep", "you"]

    async def extract(self, query: str) -> Answer:
        print(__name__)
        dialogue = "\n".join(
            self._interface.get_utterances_list()[-self._max_num_past_utterances :]
        )
        if not dialogue:
            dialogue = query

        if self._ignore_utterances(dialogue):
            return Answer.create_neutral()

        prediction = await self._connector.get_answer(
            "",
            dialogue,
            query,
        )
        return Answer(text=prediction.strip())

    def _ignore_utterances(self, dialogue: str) -> bool:
        utterance = dialogue.split("\n")[-1].split("user:")[-1].strip()
        if utterance.lower() in self._to_ignore:
            return True

        return False
