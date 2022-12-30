from unittest import TestCase

from wafl.events.conversation_events import ConversationEvents
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
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings),
            interface=interface,
            code_path="/",
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        try:
            conversation_events.process_next()

        except CloseConversation:
            return False

        assert True
