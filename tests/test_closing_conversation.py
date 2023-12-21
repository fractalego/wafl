import asyncio

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.exceptions import CloseConversation
from wafl.interface.dummy_interface import DummyInterface

wafl_example = """
rules:
  - the user thanks the bot:
    - The intention of the user is to close the conversation
    - You must answer the user by writing "<execute>close_conversation()</execute>"
"""


class TestInterruptionsToCloseConversation(TestCase):
    def test__thank_you_closes_conversation(self):
        interface = DummyInterface(
            to_utter=[
                "thank you",
            ]
        )
        config = Configuration.load_local_config()
        config.set_value("rules", wafl_example)
        conversation_events = ConversationEvents(
            config=config,
            interface=interface,
        )
        try:
            asyncio.run(conversation_events.process_next())

        except CloseConversation:
            self.assertTrue(True)
            return

        self.assertTrue(False)
