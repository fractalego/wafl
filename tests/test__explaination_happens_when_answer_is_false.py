from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.exceptions import CloseConversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_wafl_greetings = """
This bot is here to answer the user
  
INTERRUPTION the user wants to know the time
  time = get_time()
  SAY the time is {time}
  
INTERRUPTION the user says to shut up
  close_conversation()

INTERRUPTION the user wants to quit the task
  close_task()
  
""".strip()


class TestInterruptions(TestCase):
    def test_time_shut_up_does_not_interrupt_if_it_contraddicts_facts(self):
        interface = DummyInterface(["Hello", "shut up"])
        conversation = Conversation(
            SingleFileKnowledge(_wafl_greetings),
            interface=interface,
            code_path="functions",
        )
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        try:
            conversation.input()

        except CloseConversation:
            return False

        assert True
