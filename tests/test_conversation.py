from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

wafl_example = """

The user greets
  What is the user's name? username
  SAY hello to you, {username}!

The user says they can swim
  What is the user's name? username
  the user is called {username}

What is the user's hair color ? color
  What is the user's name? username
  {username} has {color} hair

the user wants to register to the newsletter
  what is the user's email? email
  REMEMBER the user's email is {email}
  SAY {email} has been added to the newsletter

This bot name is Fractalego

the user is very happy

The user's name is Bob

Bob has black hair

""".strip()


### TODO
### /1) Implement substitutions of variables within causes loop
### /2) Should you use fact_checking and qa in rule's effect? (YES)
###    /2a) Implement fact checking for non-questions
###    /2b) Implement question + forward substitution
### /3) implement SAY (conversation), REMEMBER (knowledge)
### /4) Implement questions being asked during inference
### /5) Implement temp knowledge and knowledge list

### Implement executable python code
### Implement RUN with CLI conversation (wafl run)
### Implement Server with HTML page (docker-compose up)

### 7) Refactor code and clean up ###
### 8) Investigate interplay btw substitutions and already_matched


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
        conversation.input(input_from_user)
        expected = "Hello to you, bob!"
        assert interface.utterances[-1] == expected

    def test_input_during_inference(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        input_from_user = "Can I register to the newsletter?".capitalize()
        conversation.input(input_from_user)
        expected = "Test@example.com has been added to the newsletter"
        assert interface.utterances[-1] == expected

    def test_remember_command(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        input_from_user = "Can I register to the newsletter?".capitalize()
        conversation.input(input_from_user)

        answer = conversation.input("What is the user's email")
        assert answer.text == "test@example.com"
