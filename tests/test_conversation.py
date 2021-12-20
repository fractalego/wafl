from unittest import TestCase

from wafl.conversation import Conversation
from wafl.inference import BackwardInference
from wafl.interface import BaseInterface
from wafl.knowledge import Knowledge
from wafl.qa.qa import Query

wafl_example = """

The user greets
  What is the user's name ? username
  SAY hello to you, {username}!

The user says they can swim
  What is the user's name ? username
  USER is called {username}

What is the user's hair color ? color
  What is the user's name ? username
  {username} has {color} hair

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
### 5) Implement questions being asked during inference


class DummyInterface(BaseInterface):
    def __init__(self, to_utter=None):
        self.utterances = []
        self._to_utter = to_utter

    def output(self, text: str):
        self.utterances.append(text)

    def input(self) -> str:
        return self._to_utter.pop()


class TestConversation(TestCase):

    def test_conversation(self):
        interface = DummyInterface()
        conversation = Conversation(Knowledge(wafl_example),
                                    interface=interface)
        utterance = 'Welcome to the website. How may I help you?'
        conversation.utter(utterance)
        assert interface.utterances[0] == utterance
