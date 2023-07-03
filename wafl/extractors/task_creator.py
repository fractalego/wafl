import logging
import os

from wafl.connectors.llm_task_creator_connector import LLMTaskCreatorConnector
from wafl.extractors.dataclasses import Answer, Query

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class TaskCreator:
    def __init__(self, knowledge, logger=None):
        self._connector = LLMTaskCreatorConnector()
        self._knowledge = knowledge

    async def extract(self, task: str) -> Answer:
        print(__name__)
        rules = await self._knowledge.ask_for_rule_backward(
            Query.create_from_text(task), knowledge_name="/", first_n=2
        )
        if not rules:
            return Answer.create_neutral()

        triggers = "\n".join([item.effect.text for item in rules])

        prediction = await self._connector.get_answer("", triggers, task)
        return Answer(text=prediction.strip())
