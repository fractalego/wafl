from unittest import TestCase

from wafl.events.conversation_events import ConversationEvents
from wafl.exceptions import CloseConversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_wafl_greetings = """

The user says good bye
  close_conversation()
  
""".strip()


class TestExceptions(TestCase):
    def test_runtime_warning_escapes_python_space(self):
        interface = DummyInterface(["Good bye!"])
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
            return

        assert False
