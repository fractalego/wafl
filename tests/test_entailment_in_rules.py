import os
from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from unittest import TestCase

_path = os.path.dirname(__file__)
_wafl_greetings = """

The user wants to buy something
  item = what does the user want to buy
  the user wants to buy {item} -> the user wants to buy a fruit
  SAY You want to buy fruit!

""".strip()


class TestEntailmentInRules(TestCase):
    def test__entailment_in_rule_returns_true(self):
        interface = DummyInterface(["I want to buy apples"])
        conversation = Conversation(
            SingleFileKnowledge(_wafl_greetings),
            interface=interface,
            code_path="/",
        )
        conversation.input()
        expected = "bot: You want to buy fruit!"
        assert interface.get_utterances_list()[-1] == expected
