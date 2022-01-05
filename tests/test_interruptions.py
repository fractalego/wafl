from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_greetings = """

The user says hi
  SAY Hello there!
  username = What is the user's name
  SAY Nice to meet you, {username}!
  
the user wants to know the time
  time = get_time()
  SAY the time is {time}
  
""".strip()


class TestInterruptions(TestCase):
    def ntest_time_request_does_not_interrupt(self):
        interface = DummyInterface(["Hello", "Albert"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.utterances[-1] == "Nice to meet you, albert!"

    def test_time_request_does_interrupt(self):
        interface = DummyInterface(["Hello", "what's the time?", "Albert"])
        conversation = Conversation(
            Knowledge(_wafl_greetings), interface=interface, code_path="functions"
        )
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert "The time is" in interface.utterances[-3]
        assert interface.utterances[-1] == "Nice to meet you, albert!"
