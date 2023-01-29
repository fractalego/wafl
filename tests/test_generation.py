import asyncio
import os

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)


wafl_rules = """
The user says their name
   name = what is the user's name?
   first_letter = return the first letter of the word. \
                  Examples: \
                  test, t; feast, f; {name},
                  
   SAY The first letter of your name is {first_letter} 
""".strip()


class TestGeneration(TestCase):
    def test__language_model_returns_first_letter_of_name(self):
        interface = DummyInterface(["My name is alberto"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_rules), interface=interface
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: The first letter of your name is a"
        assert interface.get_utterances_list()[-1] == expected
