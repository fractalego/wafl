from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_greetings = """
# Simple initial facts
This bot name is Computer


# Greetings commands
The user says "hi" or "hello"
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
  the user wants to close the conversation

# End the conversation
the user wants to close the conversation
  SAY good bye!
  close_conversation()

the user believes they don't need anything else
  the user wants to close the conversation

the user wishes good bye
  the user wants to end the conversation

the user says shut up
  the user wants to end the conversation


# Interruptions

the user says thank you
  Does the user want to terminate the conversation?
  the user wants to close the conversation

the user does not want to continue the task
  Do you want to continue
  close_task()

the user wants to stop
  Do you want to continue
  close_task()
    
""".strip()


class TestGreetings(TestCase):
    def test_hello_and_username(self):
        interface = DummyInterface(["Hello, my name is unknown", "Albert"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.utterances[-1] == "Nice to meet you, albert!"

    def test_hello_and_username2(self):
        interface = DummyInterface(["Hello, my name is unknown", "bob"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.utterances[-1] == "Nice to meet you, bob!"
