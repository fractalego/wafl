import asyncio

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface

wafl_example = """
rules:
  - the user says "my name is bob":
    - You must answer the user by writing "the horse is tall"
    
  - the user says their name:
    - reply casually to the conversation"
"""


class TestRules(TestCase):
    def test__rules_can_be_triggered(self):
        interface = DummyInterface(
            to_utter=[
                "my name is bob",
            ]
        )
        config = Configuration.load_local_config()
        config.set_value("rules", wafl_example)
        conversation_events = ConversationEvents(
            config=config,
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: the horse is tall"
        self.assertEqual(expected, interface.get_utterances_list()[-1])

    def test__rules_are_not_always_triggered(self):
        interface = DummyInterface(
            to_utter=[
                "my name is Frank",
            ]
        )
        config = Configuration.load_local_config()
        config.set_value("rules", wafl_example)
        conversation_events = ConversationEvents(
            config=config,
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        unexpected = "bot: the horse is tall"
        self.assertNotEqual(unexpected, interface.get_utterances_list()[-1])
