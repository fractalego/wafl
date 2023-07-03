import logging
import os

from wafl.connectors.llm_code_creator_connector import LLMCodeCreatorConnector
from wafl.extractors.dataclasses import Answer, Query
from wafl.extractors.utils import get_function_description, get_code

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class CodeCreator:
    def __init__(self, knowledge, logger=None):
        self._connector = LLMCodeCreatorConnector()
        self._knowledge = knowledge

    async def extract(self, function_and_task: str) -> Answer:
        print(__name__)
        function_and_task = function_and_task.strip()
        function_shape = get_code(function_and_task)
        task = get_function_description(function_and_task)
        prediction = await self._connector.get_answer(
            "", function_shape.strip(), task.strip()
        )
        return Answer(text=prediction.strip())
