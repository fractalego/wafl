from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_example = """

The user greets
  username = What is the user's name
  SAY hello to you, {username}!

The user says they can swim
  username = What is the user's name
  the user is called {username}

color = What is the user's hair color
  username = What is the user's name
  {username} has {color} hair

the user wants to register to the newsletter
  email = what is the user's email
  REMEMBER the user's email is {email}
  SAY {email} has been added to the newsletter

This bot name is Fractalego

the user is very happy

The user's name is Bob

Bob has black hair

""".strip()

_wafl_greetings = """
The user greets
  SAY Hello there!
  username = What is the user's name
  REMEMBER the user is called {username}
  REMEMBER the user's name is {username}
  SAY Nice to meet you, {username}!
  
The user wants to join the club
  Is the user good enough to join?
  SAY Welcome to the club!

""".strip()

_wafl_how_are_you = """

This bot name is Computer
This bot is doing well

""".strip()


class TestConversation(TestCase):
    def test_single_utterance(self):
        interface = DummyInterface()
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        assert interface.utterances[0] == utterance

    def test_say_command(self):
        interface = DummyInterface()
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        input_from_user = "hello!".capitalize()
        conversation.add(input_from_user)
        expected = "Hello to you, bob!"
        assert interface.utterances[-1] == expected

    def test_input_during_inference(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        input_from_user = "Can I register to the newsletter?".capitalize()
        conversation.add(input_from_user)
        expected = "Test@example.com has been added to the newsletter"
        assert interface.utterances[-1] == expected

    def test_remember_command(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        input_from_user = "Can I register to the newsletter?".capitalize()
        conversation.add(input_from_user)
        answer = conversation.add("What is the email of the user")
        assert answer.text == "test@example.com"

    def test_knowledge_insertion(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        input_from_user = "the user's mother is called Ada"
        conversation.add(input_from_user)
        answer = conversation.add("How is the user's mum called")
        assert answer.text == "Ada"

    def test_greeting(self):
        interface = DummyInterface(["My name is Albert", "What is my name"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        conversation.input()
        assert interface.utterances[-1] == "albert"

    def test_yes(self):
        interface = DummyInterface(["My name is Ada", "am I called Ada"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        conversation.input()
        assert "yes" in interface.utterances[-1].lower()

    def test_no(self):
        interface = DummyInterface(["My name is Albert", "Is my name Bob"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        conversation.input()
        assert "no" in interface.utterances[-1].lower()

    def test_yes_no_questions_from_bot_with_answer_yes(self):
        interface = DummyInterface(["I want to join the club", "yes"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.utterances[-1] == "Welcome to the club!"

    def test_yes_no_questions_from_bot_with_answer_no(self):
        interface = DummyInterface(["I want to join the club", "no"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.utterances[-1] == "are you good enough to join?"

    def test_hello_and_username(self):
        interface = DummyInterface(["Hello", "Albert"])
        conversation = Conversation(Knowledge(_wafl_greetings), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        assert interface.utterances[-1] == "Nice to meet you, albert!"

    def test_conversation_input_returns_false_for_trivial_input(self):
        interface = DummyInterface(["uhm what"])
        conversation = Conversation(Knowledge(""), interface=interface)
        result = conversation.input()
        assert not result

    def test_how_are_you(self):
        interface = DummyInterface(["How are you?"])
        conversation = Conversation(Knowledge(_wafl_how_are_you), interface=interface)
        conversation.input()
        assert interface.utterances[-1] == "doing well"
