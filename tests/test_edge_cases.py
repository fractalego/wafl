import asyncio

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.logger.local_file_logger import LocalFileLogger

_logger = LocalFileLogger()
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


the user wants to add something
  item = what does the user want to add?
  list_name = which list?
  the user wants to add {item} to {list_name}

# Check for trains
the user wants to check if a line is running
### TESTING COMMENTS
  line_name = which line do you want to check?
  check_tfl_line(line_name)

linename = which line is running?
  SAY {linename}
  normname = normalize_name(linename)
  check_tfl_line(normname)

is the overground running?
  check_tfl_line("overground")


# End the events
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


class TestEdgeCases(TestCase):
    def test__double_lower_case_questions_are_answered_correctly(self):
        interface = DummyInterface(["is the jubile line running"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_tube_line_rules),
            interface=interface,
            code_path="/",
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        assert "asks:" not in interface.get_utterances_list()[0]

    def test__clause_does_not_return_unknown(self):
        interface = DummyInterface(["is the jubili line running"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_tube_line_rules),
            interface=interface,
            code_path="/",
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        assert "unknown" not in interface.get_utterances_list()[-1]

    def test__no_answer_if_retrieval_is_too_sparse(self):
        interface = DummyInterface(["I will i"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_tube_line_rules),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        assert "unknown" not in interface.get_utterances_list()[-1]
