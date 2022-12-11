from unittest import TestCase

from wafl.knowledge.knowledge import Knowledge
from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface

wafl_example = """

item = what does the user want to add to the shopping list?
  the user adds something to a grocery list -> The user adds {item} to a list 
  SAY {item} will be added

item = what does the user want to add to the shopping list?
  ! the user adds something to a grocery list -> The user adds {item} to a list
  SAY {item} is not a shopping item

"""


class TestCommonSense(TestCase):
    def test__sentences_can_filter_items_positive(self):
        interface = DummyInterface(
            to_utter=[
                "Please add apples to the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "bot: Apples will be added"
        assert interface.get_utterances_list()[-1] == expected

    def test__sentences_can_filter_items_positive2(self):
        interface = DummyInterface(
            to_utter=[
                "Please add bananas to the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "bot: Bananas will be added"
        assert interface.get_utterances_list()[-1] == expected


    def test__sentences_can_filter_items_negative(self):
        interface = DummyInterface(
            to_utter=[
                "Please add no thanks to the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "bot: No thanks is not a shopping item"
        assert interface.get_utterances_list()[-1] == expected
