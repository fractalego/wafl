from unittest import TestCase

from wafl.listener.utils import choose_best_output

from wafl.config import Configuration
from wafl.interface.voice_interface import VoiceInterface
from wafl.interface.utils import not_good_enough

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
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
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        interface.add_hotwords_from_knowledge(
            Knowledge(_wafl_example), count_threshold=1
        )
        expected = [
            "JANE",
            "NAME IS",
            "IS JANE",
            "SAYS",
            "SAYS THEIR",
            "THEIR NAME",
        ]
        assert interface._listener._hotwords == expected

    def test_input_perplexity_is_not_good_enough(self):
        text = "ADD APPLES ADD ADD BUTERIES"
        assert not_good_enough(text)

    def test_input_perplexity_is_good_enough(self):
        text = "PLEASE ADD APPLES TO THE SHOPPING LIST"
        assert not not_good_enough(text)

    def test_decoder_chooses_best_output(self):
        options = (["NO", -5], ["NNO", -10])
        choice = choose_best_output(options)
        expected = "NO"
        assert choice == expected
