import asyncio
import os

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)
wafl_example = """

The user asks about the shopping list
  SAY So you do want to see it!
  
The user wants to see the todo list
  SAY No list here!

"""


class TestPolicy(TestCase):
    def test__information_is_repeated(self):
        interface = DummyInterface(
            to_utter=["What's in the shopping list", "say it again"]
        )
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_example), interface=interface
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "to see it"
        print(interface.get_utterances_list())
        assert expected in interface.get_utterances_list()[-1].lower()

    def test__policy_can_steer_conversation(self):
        interface = DummyInterface(
            to_utter=["What's in the shopping list", "I meant the todo list"]
        )
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_example), interface=interface
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "no list here!"
        print(interface.get_utterances_list())
        assert expected in interface.get_utterances_list()[-1].lower()
