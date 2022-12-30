import asyncio

from unittest import TestCase
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.qa.dataclasses import Query

wafl_example = """

The user says hello
  name = What is the user's name
  SAY Hello, {name}!  
  
item = what does the user want to add to the shopping list?
  reset_shopping_list()
  shopping_list.append(item)
  SAY {item} has been added to the list
  ! _ask_another_item

_ask_another_item
  does the user want to add another item
  item = what do you want to add to the shopping list
  SAY {item} has been added to the list
  _ask_another_item

"""


class TestKnowledge(TestCase):
    def test_exact_string(self):
        knowledge = SingleFileKnowledge(wafl_example)
        rules = knowledge.ask_for_rule_backward(
            Query(text="_ask_another_item", is_question=False)
        )
        expected = "_ask_another_item"
        assert rules[0].effect.text == expected
