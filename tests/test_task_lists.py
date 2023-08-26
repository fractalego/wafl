import asyncio
import os

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)
wafl_example = """

The user asks about the weather
  SAY the sun is shining
  
The user wants delete something
  SAY Item removed

"""


class TestTaskList(TestCase):
    def test__double_command_is_executed(self):
        interface = DummyInterface(
            to_utter=["tell me about the weather and then delete the apples"]
        )
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, wafl_example), interface=interface
        )
        asyncio.run(conversation_events.process_next())
        expected = "the sun is shining"
        assert expected in interface.get_utterances_list()[-2].lower()

        expected = "item removed"
        assert expected in interface.get_utterances_list()[-1].lower()
