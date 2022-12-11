import os
from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
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
        conversation = Conversation(
            Knowledge(_wafl_example, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        conversation.input()
        conversation.input()
        assert interface.get_utterances_list()[-1] == "bot: 0 celsius"

    def test__random_name_is_remembered(self):
        interface = DummyInterface(["My name is Albert", "What is my name"])
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        conversation.input()
        assert interface.get_utterances_list()[-1] == "bot: albert"
