import os
from unittest import TestCase


from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

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

_lists_in_functions_rules = """
item = what does the user want to add to the shopping list?
  add_shopping_list_as_function(item)
  
the user wants to know what is in the shopping list
  items = get_shopping_list_in_english()
  SAY The shopping list contains: {items}
  
the user wants to delete the shopping list
  Do you want to delete the current shopping list
  reset_shopping_list()
  SAY The shopping list has been deleted
"""


class TestNew(TestCase):
    def test__second_rule_is_not_run_if_prior_clause_fails(self):
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
        assert output.count("Do you want to remove apples from the shopping list") == 1

    def test__add_item_to_list_as_function(self):
        interface = DummyInterface(
            [
                "add apples to the shopping list",
                "yes",
                "strawberries",
                "yes",
                "bananas",
                "no",
                "what is in the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(_lists_in_functions_rules),
            interface=interface,
            code_path="functions",
        )
        while conversation.input():
            pass

        assert (
            interface.utterances[-1]
            == "The shopping list contains: strawberries, apples, bananas"
        )

    def test__yes_please_means_yes(self):
        interface = DummyInterface(
            [
                "Please delete the shopping list",
                "yes please",
                "add apples to the shopping list",
                "yes please",
                "strawberries",
                "no",
                "what is in the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(_lists_in_functions_rules),
            interface=interface,
            code_path="functions",
        )
        while conversation.input():
            pass

        print(interface.utterances)
        assert (
            interface.utterances[-1]
            == "The shopping list contains: strawberries, apples"
        )

    def test__yes_I_do_means_yes(self):
        interface = DummyInterface(
            [
                "Please delete the shopping list",
                "yes I do",
                "add apples to the shopping list",
                "yes I do",
                "strawberries",
                "no",
                "what is in the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(_lists_in_functions_rules),
            interface=interface,
            code_path="functions",
        )
        while conversation.input():
            pass
        print(interface.utterances)
        assert (
            interface.utterances[-1]
            == "The shopping list contains: strawberries, apples"
        )
