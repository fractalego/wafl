from unittest import TestCase

from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge


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
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        conversation_events.process_next()
        conversation_events.process_next()
        expected = "bot: The shopping list contains: apples, bananas"
        assert interface.get_utterances_list()[-1] == expected

    def test_say_twice_in_python_space(self):
        interface = DummyInterface(
            to_utter=[
                "Please say hello twice",
            ]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(wafl_example),
            interface=interface,
            code_path="/",
        )
        conversation_events.process_next()
        expected = [
            "bot: Please say: 'hello'",
            "bot: Your input is recorded",
            "bot: Please say: 'hello'",
            "bot: Your input is recorded",
        ]

        assert interface.get_utterances_list()[1] == expected[0]
        assert interface.get_utterances_list()[2] == expected[1]
        assert interface.get_utterances_list()[3] == expected[2]
        assert interface.get_utterances_list()[4] == expected[3]

    def test_double_fuctions(self):
        interface = DummyInterface(["Is the victoria line running"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_tube_line_rules),
            interface=interface,
            code_path="/",
        )
        conversation_events.process_next()
        assert (
            interface.get_utterances_list()[-1]
            == "bot: The victoria line is running normally"
        )
