import os
import wave
import numpy as np

from unittest import TestCase

from wafl.listener.utils import choose_best_output

from wafl.config import Configuration
from wafl.interface.voice_interface import VoiceInterface

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.listener.wav2vec2_listener import Wav2Vec2Listener

_wafl_example = """

the user says their name
  SAY nice to meet you!

the user name is Jane

""".strip()

_path = os.path.dirname(__file__)


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

    def test_decoder_chooses_best_output(self):
        options = (["NO", -1, -1], ["NNO", -0.5, -0.5])
        choice = choose_best_output(options)
        expected = "NO"
        assert choice == expected

    def test_sound_file_is_translated_correctly(self):
        f = wave.open(os.path.join(_path, "data/1002.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        listener = Wav2Vec2Listener("facebook/data2vec-audio-large-960h")
        listener.add_hotwords(["delete"])
        result = listener.input_waveform(waveform)
        expected = "DELETE BANANAS FROM THE GROCERY LIST"
        print(result)
        assert result == expected

    def test_random_sounds_are_excluded(self):
        f = wave.open(os.path.join(_path, "data/random_sounds.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        listener = Wav2Vec2Listener("facebook/data2vec-audio-large-960h")
        listener.add_hotwords(["delete"])
        result = listener.input_waveform(waveform)
        expected = ""
        assert result == expected

    def test_voice_interface_receives_config(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        assert interface.listener_model_name == config.get_value("listener_model")
