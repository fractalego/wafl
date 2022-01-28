from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.inference.backward_inference import BackwardInference
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.qa.qa import Query

wafl_example = """

item = what does the user want to add to the shopping list?
  {item} belongs to a shopping list
  SAY {item} will be added

item = what does the user want to add to the shopping list?
  ! {item} belongs to a shopping list
  SAY {item} is not a shopping item

"""


class TestNew(TestCase):
    def test_sentences_can_filter_items_positive(self):
        interface = DummyInterface(
            to_utter=[
                "Please add apples to the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "Earthworms is not a shopping list item"
        print(interface.utterances)
        assert interface.utterances[-1] == expected

    def test_sentences_can_filter_items_negative(self):
        interface = DummyInterface(
            to_utter=[
                "Please add earthworms to the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "Earthworms is not a shopping list item"
        print(interface.utterances)
        assert interface.utterances[-1] == expected
