import os

from unittest import TestCase
from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

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
        conversation = Conversation(
            Knowledge(_rules), interface=interface, code_path="functions"
        )

        while conversation.input():
            pass

        print(interface.utterances)
        assert interface.utterances[-1] == "Jubilee"
