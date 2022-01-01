from unittest import TestCase

from wafl.interface.voice_interface import VoiceInterface

from wafl.conversation.conversation import Conversation
from wafl.interface.interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_example = """

the user says their name
  SAY nice to meet you!

the user name is Jane

""".strip()


class TestVoice(TestCase):
    def test_activation(self):
        interface = DummyInterface(to_utter=["computer my name is bob"])
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        conversation.input(activation_word="computer")
        expected = "Nice to meet you!"
        assert interface.utterances[0] == expected

    def test_no_activation(self):
        interface = DummyInterface(to_utter=["my name is bob"])
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        conversation.input(activation_word="computer")
        assert interface.utterances == []

    def test_hotwords_as_input(self):
        interface = VoiceInterface()
        interface.add_hotwords_from_knowledge(Knowledge(_wafl_example))
        expected = [
            "COMPUTER",
            "JUBILEE",
            "LINE",
            "CAMDEN",
            "ADD",
            "REMOVE",
            "SHOPPING LIST",
            "APPLES",
            "JANE",
            "NAME IS",
            "IS JANE",
            "SAYS",
            "SAYS THEIR",
            "THEIR NAME",
        ]
        assert interface._listener._hotwords == expected
