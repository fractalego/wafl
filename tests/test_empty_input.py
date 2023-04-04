import asyncio

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_wafl_greetings = """

The user says their name
  SAY Hello there!
  username = What is the user's name
  SAY Nice to meet you, {username}!
  
""".strip()

_wafl_greetings2 = """

The user says hi or hello
  SAY Hello there!

""".strip()


class TestEmptyInput(TestCase):
    def test_hello_and_username(self):
        interface = DummyInterface(["Hello", "My name is Albert"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings), interface=interface
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == "bot: Nice to meet you, albert!"

    def test_empty_input_does_nothing(self):
        interface = DummyInterface(["computer"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings2), interface=interface
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        conversation_events.process_next(activation_word="computer")
        assert interface.get_utterances_list() != ["bot: Hello there!"]
