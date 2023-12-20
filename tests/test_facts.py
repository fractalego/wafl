import asyncio

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

wafl_example = """
facts:
  - the bots name is "Bob"
"""


class TestFacts(TestCase):
    def test__facts_are_retrieved(self):
        interface = DummyInterface(
            to_utter=[
                "what is your name",
            ]
        )
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_example),
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        expected = "bob"
        self.assertIn(expected, interface.get_utterances_list()[-1].lower())
