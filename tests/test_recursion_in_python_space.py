import asyncio
import os

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_rules = """
"Is the {linename} running?"
  linename = which line do you want to check?
  normname = normalize_name2(linename)
  SAY {normname}

""".strip()

_path = os.path.dirname(__file__)


class TestRecursion(TestCase):
    def test__recursion_when_normalizing_names(self):
        interface = DummyInterface(
            [
                "what line is running",
                "the jubilee line",
            ]
        )
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_rules), interface=interface, code_path="/"
        )

        while asyncio.run(conversation_events.process_next()):
            pass

        assert interface.get_utterances_list()[-1] == "bot: Jubilee"
