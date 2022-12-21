from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.exceptions import CloseConversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_greetings = """
This bot is here to answer the user unless asked to be silent

The user says hi
  SAY Hello there!
  username = What is the user's name
  SAY Nice to meet you, {username}!
  
INTERRUPTION the user wants to know the time
  time = get_time()
  SAY the time is {time}
  
INTERRUPTION the user says to shut up
  close_conversation()

INTERRUPTION the user wants to quit the task
  close_task()
  
""".strip()


class TestInterruptions(TestCase):
    def test_time_request_does_not_interrupt(self):
        interface = DummyInterface(["Hello", "Albert"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.get_utterances_list()[-1] == "bot: Nice to meet you, albert!"

    def test_time_request_does_interrupt(self):
        interface = DummyInterface(["Hello", "what's the time?", "Albert"])
        conversation = Conversation(
            Knowledge(_wafl_greetings), interface=interface, code_path="functions"
        )
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert "The time is" in interface.get_utterances_list()[-4]
        assert interface.get_utterances_list()[-1] == "bot: Nice to meet you, albert!"

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
        interface = DummyInterface(["Hello", "I want to stop the task"])
        conversation = Conversation(
            Knowledge(_wafl_greetings), interface=interface, code_path="functions"
        )
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.get_utterances_list()[-1] == "bot: Task interrupted"
