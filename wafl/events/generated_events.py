import os

from wafl.events.narrator import Narrator
from wafl.simple_text_processing.questions import is_question
from wafl.extractors.dataclasses import Query
from wafl.inference.backward_inference import BackwardInference
from wafl.exceptions import InterruptTask

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


class GeneratedEvents:
    def __init__(
        self,
        knowledge: "BaseKnowledge",
        interface: "BaseInterface",
        events: "BaseEventCreator",
        code_path=None,
        config=None,
        logger=None,
    ):
        self._inference = BackwardInference(
            knowledge, interface, Narrator(interface), code_path, logger=logger
        )
        self._knowledge = knowledge
        self._interface = interface
        self._events = events

    def output(self, text: str):
        self._interface.output(text)

    async def _process_query(self, text: str):
        query = Query(text=text, is_question=is_question(text), variable="name")
        return await self._inference.compute(query)

    async def process_next(self, activation_word: str = "") -> bool:
        events = self._events.get()
        for event in events:
            try:
                answer = await self._process_query(event)
                if answer.is_true():
                    return True

            except InterruptTask:
                self._interface.output("Task interrupted")
                return False

        return False
