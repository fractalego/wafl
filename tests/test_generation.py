import asyncio
import os

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)


wafl_rules = """
the user is Italian

The user says hello
    result = the user is Italian
    SAY {result}

The user says their name
   name = what is the user's name?
   first_letter = Return the first letter of the word {name}
   SAY {first_letter}
   SAY The first letter of your name is {first_letter} 
""".strip()


class TestGeneration(TestCase):
    def test__language_model_returns_first_letter_of_name(self):
        interface = DummyInterface(["My name is alberto"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_rules), interface=interface, code_path="/"
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: The first letter of your name is a"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected

    def test__does_not_generate_if_it_is_not_instructions(self):
        interface = DummyInterface(["Hello"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_rules), interface=interface, code_path="/"
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Yes"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected
