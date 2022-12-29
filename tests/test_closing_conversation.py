from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.exceptions import CloseConversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

wafl_example = """
_close
  close_conversation()

INTERRUPTION the user says good bye
  SAY good bye!
  _close

INTERRUPTION the user says shut up
  SAY ok
  _close

INTERRUPTION the user asks this bot to be silent
  _close

INTERRUPTION the user says: "thank you"
  _close
"""


class TestInterruptionsToCloseConversation(TestCase):
    def test__good_bye_closes_conversation(self):
        interface = DummyInterface(
            to_utter=[
                "Goodbye.",
            ]
        )
        conversation = Conversation(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        try:
            conversation.next()

        except CloseConversation:
            self.assertTrue(True)
            return

        self.assertTrue(False)

    def test__thank_you_closes_conversation(self):
        interface = DummyInterface(
            to_utter=[
                "Thank you",
            ]
        )
        conversation = Conversation(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        try:
            conversation.next()

        except CloseConversation:
            self.assertTrue(True)
            return

        self.assertTrue(False)

    def test__thanks_closes_conversation(self):
        interface = DummyInterface(
            to_utter=[
                "Thanks.",
            ]
        )
        conversation = Conversation(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        try:
            conversation.next()

        except CloseConversation:
            self.assertTrue(True)
            return

        self.assertTrue(False)
