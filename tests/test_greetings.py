import asyncio

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_wafl_greetings = """
# Simple initial facts
This bot name is Computer


# Greetings commands
The user greets
  ! the user has introduced themselves
  SAY Hello there!
  username = What is the user's name
  REMEMBER the user is called {username}
  REMEMBER the user's name is {username}
  REMEMBER the user introduced themselves
  SAY Nice to meet you, {username}!


# Time commands
the user asks for the time
  time = get_time()
  SAY the time is {time}


# voice bootstrapping
the user wants to record their voice
  do you want to record your voice?
  record_utterances()
  the user wants to close the events

# End the events
the user wants to close the events
  SAY good bye!
  close_conversation()

the user believes they don't need anything else
  the user wants to close the events

the user wishes good bye
  the user wants to end the events

the user says shut up
  the user wants to end the events


# Interruptions

the user says thank you
  Does the user want to terminate the events?
  the user wants to close the events

the user does not want to continue the task
  Do you want to continue
  close_task()

the user wants to stop
  Do you want to continue
  close_task()
    
""".strip()


class TestGreetings(TestCase):
    def test_hello_and_username(self):
        interface = DummyInterface(["Hello", "Albert"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, _wafl_greetings), interface=interface
        )
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        asyncio.run(conversation_events.process_next())
        assert interface.get_utterances_list()[-1] == "bot: Nice to meet you, albert!"

    def test_hello_and_username2(self):
        interface = DummyInterface(["Hello", "bob"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, _wafl_greetings), interface=interface
        )
        utterance = "Welcome to the website. How may I help you?"
        asyncio.run(interface.output(utterance))
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == "bot: Nice to meet you, bob!"
