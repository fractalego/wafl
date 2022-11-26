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
        expected = "bot: The shopping list contains: apples, bananas"
        assert interface.get_utterances_list()[-1] == expected

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
            "bot: Please say: 'hello'",
            "bot: Your input is recorded",
            "bot: Please say: 'hello'",
            "bot: Your input is recorded",
        ]
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[1] == expected[0]
        assert interface.get_utterances_list()[2] == expected[1]
        assert interface.get_utterances_list()[3] == expected[2]
        assert interface.get_utterances_list()[4] == expected[3]

    def test_double_fuctions(self):
        interface = DummyInterface(["Is the victoria line running"])
        conversation = Conversation(
            Knowledge(_tube_line_rules), interface=interface, code_path="functions"
        )
        conversation.input()
        assert interface.get_utterances_list()[-1] == "bot: The victoria line is running normally"
