import asyncio

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.exceptions import CloseConversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge


wafl_example = """
This bot is here to answer the user.

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


class TestLanguageInFunctions(TestCase):
    def test__good_bye_closes_conversation(self):
        interface = DummyInterface(
            to_utter=[
                "Goodbye.",
            ]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        try:
            asyncio.run(conversation_events.process_next())

        except CloseConversation:
            self.assertTrue(True)
            return

        self.assertTrue(False)

    def test__thank_you_closes_conversation(self):
        interface = DummyInterface(
            to_utter=[
                "Thank you.",
            ]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        try:
            asyncio.run(conversation_events.process_next())

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
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        try:
            asyncio.run(conversation_events.process_next())

        except CloseConversation:
            self.assertTrue(True)
            return

        self.assertTrue(False)
