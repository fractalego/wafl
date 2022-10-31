from unittest import TestCase

from wafl.knowledge.knowledge import Knowledge

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface

from wafl.qa.common_sense import CommonSense

wafl_example = """

item = what does the user want to add to the shopping list?
  '{item}' can be a part of a grocery list
  SAY {item} will be added

item = what does the user want to add to the shopping list?
  ! {item} can be a part of a grocery list
  SAY {item} is not a shopping item

"""


class TestCommonSense(TestCase):
    def test_common_sense_positive(self):
        claim = "'pasta' can be a part of a grocery list"
        common_sense = CommonSense()
        answer = common_sense.claim_makes_sense(claim)
        assert answer.text == "True"

    def test_common_sense_negative(self):
        claim = "'no thanks' can be a part of a grocery list"
        common_sense = CommonSense()
        answer = common_sense.claim_makes_sense(claim)
        assert answer.text == "False"

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
        expected = "Apples will be added"
        assert interface.utterances[-1] == expected

    def test_sentences_can_filter_items_negative(self):
        interface = DummyInterface(
            to_utter=[
                "Please add no thanks to the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = "No thanks is not a shopping item"
        assert interface.utterances[-1] == expected
