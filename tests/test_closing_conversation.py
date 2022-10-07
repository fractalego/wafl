from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.exceptions import CloseConversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.parsing.preprocess import (
    create_preprocessed,
    remove_preprocessed,
    import_module,
)

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
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        try:
            conversation.input()

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
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        try:
            conversation.input()

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
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        try:
            conversation.input()

        except CloseConversation:
            self.assertTrue(True)
            return

        self.assertTrue(False)
