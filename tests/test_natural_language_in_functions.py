from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
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
  
the user wants this bot to say hello twice
  say_twice()
"""

_tube_line_rules = """
linename = which line is running?
  SAY RUNNING
  normname = normalize_name(linename)
  SAY {normname}
  check_tfl_line(normname)

is the overground running?
  check_tfl_line("overground")

is the dlr running?
  check_tfl_line("dlr")

""".strip()


class TestLanguageInFunctions(TestCase):
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

    def test_say_twice_in_python_space(self):
        interface = DummyInterface(
            to_utter=[
                "Please say hello twice",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="functions"
        )
        conversation.input()
        expected = [
            "Please say: 'hello'",
            "Your input is recorded",
            "Please say: 'hello'",
            "Your input is recorded",
        ]
        assert interface.utterances == expected

    def test_double_fuctions(self):
        interface = DummyInterface(["Is the victoria line running"])
        conversation = Conversation(
            Knowledge(_tube_line_rules), interface=interface, code_path="functions"
        )
        conversation.input()
        assert interface.utterances[-1] == "The victoria line is running normally"
