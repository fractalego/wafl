import asyncio
import os

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.filter.base_filter import BaseAnswerFilter
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)


wafl_rules = """
The user says hello
    SAY hello to the user

""".strip()


class TestDecorator(TestCase):
    def test__filter(self):
        config = Configuration.load_local_config()
        interface = DummyInterface(
            ["Hello"],
            output_filter=BaseAnswerFilter(config),
        )

        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_rules),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Hello to you."
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected
