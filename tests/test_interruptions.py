import asyncio

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.exceptions import CloseConversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_wafl_greetings = """
This bot is here to answer the user unless asked to be silent

The user says hi
  SAY Hello there!
  username = What is the user's name
  SAY Nice to meet you, {username}!
  
INTERRUPTION the user wants to know the time
  time = get_time()
  SAY the time is {time}
  
INTERRUPTION the user says to shut up
  close_conversation()

INTERRUPTION the user wants to quit the task
  close_task()
  
""".strip()


class TestInterruptions(TestCase):
    def test_time_request_does_not_interrupt(self):
        interface = DummyInterface(["Hello", "Albert"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings), interface=interface
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        assert interface.get_utterances_list()[-1] == "bot: Nice to meet you, albert!"

    def test_time_request_does_interrupt(self):
        interface = DummyInterface(["Hello", "what's the time?", "Albert"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings),
            interface=interface,
            code_path="/",
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        assert "The time is" in interface.get_utterances_list()[-4]
        assert interface.get_utterances_list()[-1] == "bot: Nice to meet you, albert!"

    def test_time_shut_up_does_interrupt(self):
        interface = DummyInterface(["Hello", "shut up"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings),
            interface=interface,
            code_path="/",
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        try:
            asyncio.run(conversation_events.process_next())

        except CloseConversation:
            return

        assert False

    def test_task_interrupt_task_does_interrupt(self):
        interface = DummyInterface(["Hello", "I want to stop the task"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings),
            interface=interface,
            code_path="/",
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        asyncio.run(conversation_events.process_next())
        assert interface.get_utterances_list()[-1] == "bot: Task interrupted"
