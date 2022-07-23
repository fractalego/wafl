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

_wafl_greetings2 = """

The user says hi or hello
  SAY Hello there!

""".strip()


class TestEmptyInput(TestCase):
    def test_hello_and_username(self):
        interface = DummyInterface(["Hello", "My name is Albert"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        conversation.input()
        assert interface.utterances[-1] == "Nice to meet you, albert!"

    def test_empty_input_does_nothing(self):
        interface = DummyInterface(["computer"])
        conversation = Conversation(Knowledge(_wafl_greetings2), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input(activation_word="computer")
        assert interface.utterances != ["Hello there!"]
