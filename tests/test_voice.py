from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_example = """

the user says their name
  SAY nice to meet you!

""".strip()


class TestVoice(TestCase):
    def test_activation(self):
        interface = DummyInterface(to_utter=['computer my name is bob'])
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        conversation.input(activation_word='computer')
        expected = 'Nice to meet you!'
        assert interface.utterances[0] == expected

    def test_no_activation(self):
        interface = DummyInterface(to_utter=['my name is bob'])
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        conversation.input(activation_word='computer')
        assert interface.utterances == []
