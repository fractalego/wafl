import asyncio
import os

from unittest import TestCase
from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.events.generated_events import GeneratedEvents
from wafl.events.events_from_function_list import EventsCreatorFromFunctionList
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.scheduler.conversation_loop import ConversationLoop
from wafl.scheduler.generated_event_loop import GeneratedEventLoop
from wafl.scheduler.scheduler import Scheduler

_path = os.path.dirname(__file__)
_logger = LocalFileLogger()


def return_four_past_seven():
    return "The time is 7,04"


_wafl_example = """
It is 7,04
  SAY It's 4 past seven!
  keyboard_interrupt()
  
the user greets
  keyboard_interrupt()
""".strip()


class TestScheduler(TestCase):
    def test__conversation_loop_can_run(self):
        config = Configuration.load_local_config()
        knowledge = ProjectKnowledge(config, "rules.wafl", logger=_logger)
        interface = DummyInterface(["hello!"])
        conversation_events = ConversationEvents(
            knowledge,
            interface=interface,
            code_path=knowledge.get_dependencies_list(),
            config=config,
            logger=_logger,
        )
        conversation_loop = ConversationLoop(
            interface,
            conversation_events,
            _logger,
            activation_word="",
            max_misses=3,
        )
        asyncio.run(conversation_loop.run())
        expected = ["user: hello !", "bot: Good bye!"]
        self.assertEqual(expected, interface.get_utterances_list())

    def test__scheduler_can_run_with_conversation_loop(self):
        config = Configuration.load_local_config()
        knowledge = ProjectKnowledge(config, "rules.wafl", logger=_logger)
        interface = DummyInterface(["hello!"])
        conversation_events = ConversationEvents(
            knowledge,
            interface=interface,
            code_path=knowledge.get_dependencies_list(),
            config=config,
            logger=_logger,
        )
        conversation_loop = ConversationLoop(
            interface,
            conversation_events,
            _logger,
            activation_word="",
        )
        scheduler = Scheduler([conversation_loop])
        scheduler.run()
        expected = ["user: hello !", "bot: Good bye!"]
        self.assertEqual(expected, interface.get_utterances_list())

    async def test__scheduler_can_run_with_conversation_and_event_loop__no_trigger_from_events(
        self,
    ):
        config = Configuration.load_local_config()
        knowledge = ProjectKnowledge(config, "rules.wafl", logger=_logger)
        interface = DummyInterface(["hello!"])
        conversation_events = ConversationEvents(
            knowledge,
            interface=interface,
            code_path=knowledge.get_dependencies_list(),
            config=config,
            logger=_logger,
        )
        conversation_loop = ConversationLoop(
            interface,
            conversation_events,
            _logger,
            activation_word="",
        )
        event_loop = GeneratedEventLoop(
            interface,
            GeneratedEvents(
                knowledge,
                events=EventsCreatorFromFunctionList([return_four_past_seven]),
                interface=interface,
                code_path=knowledge.get_dependencies_list(),
                logger=_logger,
            ),
            logger=_logger,
        )
        async with asyncio.timeout(3):
            scheduler = Scheduler([conversation_loop, event_loop])
            scheduler.run()
            expected = ["user: hello !", "bot: Good bye!"]

        self.assertEqual(expected, interface.get_utterances_list())

    async def test__scheduler_can_run_with_conversation_and_event_loop__does_trigger_from_events(
        self,
    ):
        config = Configuration.load_local_config()
        knowledge = SingleFileKnowledge(config, _wafl_example, logger=_logger)
        interface = DummyInterface(["hello!"])
        conversation_events = ConversationEvents(
            knowledge,
            interface=interface,
            config=config,
            code_path="/",
            logger=_logger,
        )
        conversation_loop = ConversationLoop(
            interface,
            conversation_events,
            _logger,
            activation_word="",
        )
        event_loop = GeneratedEventLoop(
            interface,
            GeneratedEvents(
                config,
                knowledge,
                events=EventsCreatorFromFunctionList([return_four_past_seven]),
                code_path="/",
                interface=interface,
                logger=_logger,
            ),
            logger=_logger,
        )
        async with asyncio.timeout(3):
            scheduler = Scheduler([event_loop, conversation_loop])
            scheduler.run()
            expected = ["bot: It's 4 past seven!", "user: hello !", "bot: Good bye!"]

        self.assertEqual(expected, interface.get_utterances_list())
