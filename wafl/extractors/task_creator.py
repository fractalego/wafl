import logging
import os

from wafl.connectors.bridges.llm_task_creator_bridge import LLMTaskCreatorBridge
from wafl.extractors.dataclasses import Answer, Query

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class TaskCreator:
    def __init__(self, config, knowledge, logger=None):
        self._connector = LLMTaskCreatorBridge(config)
        self._knowledge = knowledge
        self._logger = logger

    async def extract(self, task: str) -> Answer:
        print(__name__)
        if self._logger:
            self._logger.write("TaskCreator: asking for rules")

        rules = await self._knowledge.ask_for_rule_backward(
            Query.create_from_text(task), knowledge_name="/", first_n=15
        )
        rules = [rule for rule in rules if not rule.effect.is_interruption]
        if self._logger:
            self._logger.write("Rules found")
            for rule in rules:
                self._logger.write(str(rule))

        triggers = "\n".join(["- " + item.effect.text for item in rules])
        prediction = await self._connector.get_answer("", triggers, task)
        return Answer(text=prediction.strip())
