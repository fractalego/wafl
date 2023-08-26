import asyncio
import os

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.extractors.dataclasses import Query

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


class TestShoppingList(TestCase):
    def test_no_activation(self):
        config = Configuration.load_local_config()
        knowledge = SingleFileKnowledge(config, _rules)
        results = asyncio.run(
            knowledge.ask_for_rule_backward(
                Query(
                    text="The user says: 'remove apples from the shopping list.'",
                    is_question=False,
                )
            )
        )
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
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, _rules), interface=interface, code_path="/"
        )
        asyncio.run(conversation_events.process_next())
        asyncio.run(conversation_events.process_next())
        output = "\n".join(interface.get_utterances_list())
        assert output.count("Do you want to remove apples from the shopping list") == 1
