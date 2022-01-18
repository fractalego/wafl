from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_greetings = """

# Simple initial facts
This bot name is Computer

""".strip()

_tube_line_rules = """

# Simple initial facts
This bot is doing well

This bot is called Computer


# Greetings commands
The user says "bring yourself online"
  SAY Hello there!

the user asks "How are you"
  SAY All is good thanks


# Time commands
the user asks for the time
  time = get_time()
  SAY the time is {time}


# Shopping list

item = what does the user want to add to the shopping list?
  add_shopping_list(item)
  SAY {item} has been added to the list
  ! _ask_another_item
  items = get_shopping_list_in_english()
  SAY the shopping list now contains: {items}


_ask_another_item
  does the user want to add another item
  item = what do you want to add to the shopping list
  add_shopping_list(item)
  SAY {item} has been added to the list
  _ask_another_item

the user wants to delete the shopping list
  Do you want to delete the current shopping list
  reset_shopping_list()
  SAY The shopping list has been deleted

the user wants to know what is in the shopping list
  items = get_shopping_list_in_english()
  SAY The shopping list contains: {items}

"What should I buy"
  the user wants to know what is in the shopping list


# Check for trains
the user wants to check if a line is running
### WHY DOES IT WORK IF I PUT A ?
  line_name = which line do you want to check?
  check_tfl_line(line_name)

linename = which line is running?
  SAY {linename}
  normname = normalize_name(linename)
  check_tfl_line(normname)

is the overground running?
  check_tfl_line("overground")


# End the conversation
_close
  close_conversation()

the user believes they don't need anything else
  SAY ok
  _close

the user says good bye
  SAY good bye!
  _close

the user says shut up
  SAY ok
  _close

the user asks this bot to be silent
  _close

the user says: "thank you this is all"
  _close

# Interruptions


the user does not want to continue the task
  ! Do you want to continue
  close_task()

the user wants to stop
  ! Do you want to continue
  close_task())

""".strip()


class TestExceptions(TestCase):
    def ntest_runtime_warning_escapes_python_space(self):
        interface = DummyInterface(["How are you!"])
        conversation = Conversation(
            Knowledge(_wafl_greetings), interface=interface, code_path="functions"
        )
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)

        conversation.input()
        expected = "It is a bot name"
        assert interface.utterances[-1] == expected

    def ntest_double_lower_case_questions_are_answered_correctly(self):
        interface = DummyInterface(["is the jubile line running"])
        conversation = Conversation(
            Knowledge(_tube_line_rules), interface=interface, code_path="functions"
        )
        conversation.input()
        assert "asks:" not in interface.utterances[0]

    def test_clause_does_not_return_unknown(self):
        interface = DummyInterface(["is the jubili line running"])
        conversation = Conversation(
            Knowledge(_tube_line_rules), interface=interface, code_path="functions"
        )
        conversation.input()
        assert "unknown" not in interface.utterances[-1]
