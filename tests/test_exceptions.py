from unittest import TestCase

from wafl.conversation.conversation import Conversation
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
            return

        assert False
