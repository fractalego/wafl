from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.exceptions import CloseConversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_greetings = """

The user says hi
  SAY Hello there!
  username = What is the user's name
  SAY Nice to meet you, {username}!
  
INTERRUPTION the user wants to know the time
  time = get_time()
  SAY the time is {time}
  
INTERRUPTION the user says to shut up
  close_conversation()

INTERRUPTION the user does not want to continue the task
  close_task()
  
""".strip()


class TestInterruptions(TestCase):
    def test_time_request_does_not_interrupt(self):
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

    def test_time_shut_up_does_interrupt(self):
        interface = DummyInterface(["Hello", "shut up"])
        conversation = Conversation(
            Knowledge(_wafl_greetings), interface=interface, code_path="functions"
        )
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        try:
            conversation.input()

        except CloseConversation:
            return

        assert False

    def test_task_interrupt_task_does_interrupt(self):
        interface = DummyInterface(["Hello", "I don't want to continue the task"])
        conversation = Conversation(
            Knowledge(_wafl_greetings), interface=interface, code_path="functions"
        )
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.utterances[-1] == "Task interrupted"
