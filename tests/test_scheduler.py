import os
from unittest import TestCase

from wafl.config import Configuration
from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.scheduler.scheduler import Scheduler

_path = os.path.dirname(__file__)
_logger = LocalFileLogger()


class TestScheduler(TestCase):
    def test__scheduler_can_run(self):
        #### ADD EXTERNAL FUNCTIONS TO SCHEDULERS
        ####  - CREATE INTERFACE FOR THESE FUNCTIONS
        ####  - HIBRID INTERFACE SHOULD USE LIST OF INTERFACES
        ####     - USE ASYNCIO
        ####
        #### ADD CAPABILITY OF ADDING AND REMOVING RULES

        config = Configuration.load_local_config()
        knowledge = ProjectKnowledge("rules.wafl", logger=_logger)
        interface = DummyInterface(["hello!"])
        conversation = Conversation(
            knowledge,
            interface=interface,
            code_path=knowledge.get_dependencies_list(),
            config=config,
            logger=_logger,
        )
        scheduler = Scheduler(
            interface,
            conversation,
            _logger,
            activation_word="",
        )
        scheduler.run(max_misses=3)
