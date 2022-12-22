from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge


wafl_dependency = """
#using greetings

The user greets
  person = who did the user greet
  the user salutes {person}

""".strip()


class TestNegations(TestCase):
    def test__(self):
        interface = DummyInterface(
            to_utter=[
                "Hello my friend",
            ]
        )
        conversation = Conversation(
            SingleFileKnowledge(wafl_dependency), interface=interface
        )
        conversation.input()
        expected = "bot: Hello, my friend"
        assert interface.get_utterances_list()[-1] == expected
