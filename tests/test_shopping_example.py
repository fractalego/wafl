import os
import wave
from unittest import TestCase

import numpy as np

from wafl.conversation.conversation import Conversation
from wafl.inference.backward_inference import BackwardInference
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.listener.wav2vec2_listener import Wav2Vec2Listener
from wafl.qa.qa import Query

_path = os.path.dirname(__file__)

_rules = """

item = what does the user want to add to the shopping list?
  add_shopping_list(item)
  SAY {item} has been added to the list
  ! _ask_another_item

item = what does the user want to add to the shopping list?
  add_shopping_list(item)
  !{item} can be part of a shopping list
  SAY Please speak more clearly

item = what does the user want to remove from the shopping list?
  remove_from_shopping_list(item)
  items = get_shopping_list_in_english()

_ask_another_item
  does the user want to add another item
  item = what do you want to add to the shopping list
  add_shopping_list(item)
  SAY {item} has been added to the list
  _ask_another_item

_ask_another_item
  does the user want to add another item
  item = what do you want to add to the shopping list
  !{item} can be part of a shopping list
  SAY {item} cannot be part of a shopping list
  _ask_another_item

"remove an item from the shopping list"
  item = What do you want to remove?
  remove_from_shopping_list(item)
  items = get_shopping_list_in_english()

the user wants to delete the shopping list
  Do you want to delete the current shopping list
  reset_shopping_list()
  SAY The shopping list has been deleted

the user wants to know what is in the shopping list
  items = get_shopping_list_in_english()
  SAY The shopping list contains: {items}

"What should I buy"
  the user wants to know what is in the shopping list

"""


class TestNew(TestCase):
    def test_no_activation(self):
        knowledge = Knowledge(_rules)
        results = knowledge.ask_for_rule_backward(
            Query(
                text="The user says: 'remove apples from the shopping list.'",
                is_question=False,
            )
        )
        print(len(results))
        assert len(results) == 2

    def test_second_rule_is_not_run_if_prior_clause_fails(self):
        interface = DummyInterface(
            [
                "add apples to the shopping list",
                "no",
                "remove apples from the shopping list",
                "no",
            ]
        )
        conversation = Conversation(
            Knowledge(_rules), interface=interface, code_path="functions"
        )
        conversation.input()
        conversation.input()
        output = "\n".join(interface.utterances)
        print(interface.utterances)
        assert output.count("Do you want to remove apples from the shopping list") == 1
