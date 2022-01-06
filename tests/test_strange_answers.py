from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_greetings = """

# Simple initial facts
This bot name is Computer

""".strip()


class TestExceptions(TestCase):
    def test_runtime_warning_escapes_python_space(self):
        interface = DummyInterface(["How are you!"])
        conversation = Conversation(
            Knowledge(_wafl_greetings), interface=interface, code_path="functions"
        )
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)

        conversation.input()
        expected = "It is a bot name."
        print(interface.utterances)
        assert interface.utterances[-1] == expected
