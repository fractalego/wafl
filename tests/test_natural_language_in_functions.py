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
  
item = what does the user want to add to the shopping list?
  reset_shopping_list()
  shopping_list.append(item)
  SAY {item} has been added to the list
  append_until_user_is_done()
  

the user wants to know what is in the shopping list
  items = get_shopping_list_in_english()
  SAY The shopping list contains: {items}  

"""


class TestLanguageInFunctions(TestCase):
    def test_preprocessing(self):
        create_preprocessed("functions")
        remove_preprocessed("functions")

    def test_import_preprocessed_module(self):
        create_preprocessed("functions")
        import_module("functions")
        remove_preprocessed("functions")

    def test_executables(self):
        interface = DummyInterface(
            to_utter=[
                "Add apples to the shopping list",
                "yes",
                "Please add bananas to the shopping list",
                "no",
                "What's in the shopping list",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        conversation.input()
        expected = "The shopping list contains: apples, bananas"
        assert interface.utterances[-1] == expected
