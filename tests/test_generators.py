import asyncio
import os

from datetime import datetime
from unittest import TestCase

from wafl.events.generated_events import GeneratedEvents
from wafl.generators.generator_from_function_list import GeneratorFromFunctionList
from wafl.generators.generator_from_module_name import GeneratorFromModuleName
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.logger.local_file_logger import LocalFileLogger

_path = os.path.dirname(__file__)
_logger = LocalFileLogger()

_wafl_example = """
It is 7,05
  SAY Hello there!
""".strip()


def function_that_returns_time():
    now = datetime.now()
    minutes = int(now.strftime("%M"))
    hour = int(now.strftime("%H"))
    return f"The time is {hour}:{minutes}"


def return_five_past_seven():
    return "the time is 7,05"


def return_four_past_seven():
    return "the time is 7,04"


class TestGenerators(TestCase):
    def test__generator_correctly_uses_argument_functions(self):
        generator = GeneratorFromFunctionList([function_that_returns_time])
        expected = function_that_returns_time()
        predicted = generator.get()[0]
        self.assertEqual(expected, predicted)

    def test__generator_can_trigger_rule(self):
        interface = DummyInterface()
        generated_events = GeneratedEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            generators=GeneratorFromFunctionList([return_five_past_seven]),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(generated_events.process_next())

        expected = "bot: Hello there!"
        assert interface.get_utterances_list()[-1] == expected

    def test__generator_does_not_trigger_rule(self):
        interface = DummyInterface()
        generated_events = GeneratedEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            generators=GeneratorFromFunctionList([return_four_past_seven]),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(generated_events.process_next())
        expected = []
        assert interface.get_utterances_list() == expected

    def test__generator_functions_can_be_loaded_from_file(self):
        interface = DummyInterface()
        generated_events = GeneratedEvents(
            SingleFileKnowledge(_wafl_example, logger=_logger),
            generators=GeneratorFromModuleName("generators"),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(generated_events.process_next())
        expected = ['bot: Hello there!']
        assert interface.get_utterances_list() == expected
