import asyncio
import os

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from unittest import TestCase

_path = os.path.dirname(__file__)
_wafl_greetings = """

The user wants to buy something
  item = what does the user want to buy
  the user wants to buy a fruit:-the user wants to buy {item}
  SAY You want to buy fruit!

""".strip()


class TestEntailmentInRules(TestCase):
    def test__entailment_in_rule_returns_true(self):
        interface = DummyInterface(["I want to buy apples"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            SingleFileKnowledge(config, _wafl_greetings),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: You want to buy fruit!"
        assert interface.get_utterances_list()[-1] == expected
