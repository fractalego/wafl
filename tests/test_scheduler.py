import asyncio
import os

from unittest import TestCase
from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.scheduler.conversation_loop import ConversationLoop

_path = os.path.dirname(__file__)
_logger = LocalFileLogger()


class TestScheduler(TestCase):
    def test__scheduler_can_run(self):
        config = Configuration.load_local_config()
        knowledge = ProjectKnowledge("rules.wafl", logger=_logger)
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
        asyncio.run(conversation_loop.run(max_misses=3))
