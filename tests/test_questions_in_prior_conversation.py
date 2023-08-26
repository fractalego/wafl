import asyncio
import os

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.logger.local_file_logger import LocalFileLogger

_path = os.path.dirname(__file__)

_logger = LocalFileLogger()

_wafl_example = """

The user greets
  SAY the weather is very cold
  SAY the temperature today is 0 celsius

""".strip()


class TestAnswerInConversation(TestCase):
    def test__temperature_is_remembered(self):
        interface = DummyInterface(["Hello!", "What is the temperature today?"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, _wafl_example, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "0"
        print(interface.get_utterances_list())
        assert expected in interface.get_utterances_list()[-1]

    def test__random_name_is_remembered(self):
        interface = DummyInterface(["My name is Albert", "What is my name"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, _wafl_example), interface=interface
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        expected = "albert"
        assert expected in interface.get_utterances_list()[-1].lower()
