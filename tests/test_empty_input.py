from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_greetings = """

The user says their name
  SAY Hello there!
  username = What is the user's name
  SAY Nice to meet you, {username}!
  
""".strip()


class TesEmptyInput(TestCase):
    def test_hello_and_username(self):
        interface = DummyInterface(["Hello, my name is unknown", "", "", "Albert"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.utterances[-1] == "Nice to meet you, albert!"
