from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface import DummyInterface
from wafl.knowledge import Knowledge

wafl_example = """

The user greets
  What is the user's name? username
  SAY hello to you, {username}!

The user says they can swim
  What is the user's name? username
  USER is called {username}

What is the user's hair color ? color
  What is the user's name? username
  {username} has {color} hair

the user wants to register to the newsletter
  what is the user's email? email
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

### 3) Investigate interplay btw substitutions and already_matched

### 4) implement SAY (conversation), REMEMBER (knowledge)
### /5) Implement questions being asked during inference
### 6) Implement temp knowledge and knowledge list


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
        conversation.input(f"The user says: {input_from_user}")
        expected = "Hello to you, bob!"
        assert interface.utterances[-1] == expected

    def test_input_during_inference(self):
        interface = DummyInterface(to_utter=["test@example.com"])
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        input_from_user = "Can I register to the newsletter?".capitalize()
        conversation.input(f"The user says: {input_from_user}")
        expected = "Test@example.com has been added to the newsletter"
        print(interface.utterances)
        assert interface.utterances[-1] == expected
