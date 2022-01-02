from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.parsing.preprocess import (
    create_preprocessed,
    remove_preprocessed,
    import_module,
)

wafl_example = """
  
the user wants to know what is in the shopping list
  Does the user want to see the shopping list
  SAY So you do want to see it!  

"""


class TestNegations(TestCase):
    def test_simple_yes(self):
        interface = DummyInterface(
            to_utter=[
                "What's in the shopping list",
                "yes",
            ]
        )
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        conversation.input()
        expected = "So you do want to see it!"
        assert interface.utterances[-1] == expected

    def test_simple_no(self):
        interface = DummyInterface(
            to_utter=[
                "I want to know what the shopping list contains",
                "no",
            ]
        )
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        conversation.input()
        expected = "do you want to see the shopping list"
        assert interface.utterances[-1] == expected

    def test_no_thanks(self):
        interface = DummyInterface(
            to_utter=[
                "I want to know what the shopping list contains",
                "no thanks",
            ]
        )
        conversation = Conversation(Knowledge(wafl_example), interface=interface)
        conversation.input()
        expected = "do you want to see the shopping list"
        assert interface.utterances[-1] == expected
