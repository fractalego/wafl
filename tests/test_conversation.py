from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

wafl_example = """

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


### TODO
### Implement executable python code
### Implement RUN with CLI conversation (wafl run)
### Implement Server with HTML page (docker-compose up)

### Refactor code and clean up ###
### Investigate interplay btw substitutions and already_matched


class TestConversation(TestCase):
    def test_single_utterance(self):
        interface = DummyInterface()
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        assert interface.utterances[0] == utterance

    def test_say_command(self):
        interface = DummyInterface()
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        input_from_user = "hello!".capitalize()
        conversation.add(input_from_user)
        expected = "Hello to you, bob!"
        assert interface.utterances[-1] == expected

    def test_input_during_inference(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        input_from_user = "Can I register to the newsletter?".capitalize()
        conversation.add(input_from_user)
        expected = "Test@example.com has been added to the newsletter"
        assert interface.utterances[-1] == expected

    def test_remember_command(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        input_from_user = "Can I register to the newsletter?".capitalize()
        conversation.add(input_from_user)

        answer = conversation.add("What is the email of the user")
        assert answer.text == "test@example.com"

    def test_knowledge_insertion(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        input_from_user = "the user's mother is called Ada"
        conversation.add(input_from_user)
        answer = conversation.add("How is the user's mum called")
        assert answer.text == "Ada"
