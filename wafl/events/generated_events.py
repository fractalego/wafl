import os

from wafl.answerer.inference_answerer import InferenceAnswerer
from wafl.events.narrator import Narrator
from wafl.inference.backward_inference import BackwardInference
from wafl.events.utils import input_is_valid
from wafl.exceptions import InterruptTask

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"


class GeneratedEvents:
    def __init__(
        self,
        knowledge: "BaseKnowledge",
        interface: "BaseInterface",
        generators: "StringGenerator",
        code_path=None,
        config=None,
        logger=None,
    ):
        self._answerer = InferenceAnswerer(
            interface,
            BackwardInference(
                knowledge, interface, Narrator(interface), code_path, logger=logger
            ),
            logger,
        )
        self._knowledge = knowledge
        self._interface = interface
        self._generators = generators

    def output(self, text: str):
        self._interface.output(text)

    async def _process_query(self, text: str):
        await self._answerer.answer(text)

    async def process_next(self, activation_word: str = "") -> bool:
        for event in self._generators.get():
            try:
                await self._process_query(event)
                return True

            except InterruptTask:
                self._interface.output("Task interrupted")
                return False

        return False
