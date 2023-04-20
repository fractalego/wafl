import logging
import os

from wafl.connectors.gptj_task_extractor_connector import GPTJTaskExtractorConnector
from wafl.extractors.dataclasses import Answer

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class TaskExtractor:
    def __init__(self, interface, logger=None):
        self._interface = interface
        self._connector = GPTJTaskExtractorConnector()
        self._max_num_past_utterances = 3

    async def extract(self, query: str):
        dialogue = "\n".join(
            self._interface.get_utterances_list()[-self._max_num_past_utterances :]
        )
        if not dialogue:
            dialogue = query

        prediction = await self._connector.get_answer(
            "",
            dialogue,
            query,
        )
        return Answer(text=prediction.strip())
