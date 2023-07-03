import asyncio
import os

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)
_wafl_example = """
the user wants to create a new rule
  REMEMBER the user says "hello" :- SAY Hello there!; SAY This rule was created
  SAY A rule was created 
"""


class TestRulesCreation(TestCase):
    def test__one_line_rule_can_be_created(self):
        interface = DummyInterface()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_example),
            interface=interface,
        )
        input_from_user = "I need you to create a new rule"
        asyncio.run(conversation_events._process_query(input_from_user))
        expected = "bot: A rule was created"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected

        interface.reset_history()
        input_from_user = "Hello"
        asyncio.run(conversation_events._process_query(input_from_user))
        expected = ["bot: Hello there!", "bot: This rule was created"]
        assert interface.get_utterances_list()[-2:] == expected
