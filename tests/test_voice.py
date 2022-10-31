import os
import wave
import numpy as np

from unittest import TestCase

from wafl.config import Configuration
from wafl.interface.voice_interface import VoiceInterface

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.listener.whisper_listener import WhisperListener

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
        conversation.check_understanding(True)
        conversation.input(activation_word="computer")
        expected = "Nice to meet you!"
        assert interface.utterances[0] == expected

    def test_no_activation(self):
        interface = DummyInterface(to_utter=["my name is bob"])
        conversation = Conversation(Knowledge(_wafl_example), interface=interface)
        conversation.check_understanding(False)
        conversation.input(activation_word="computer")
        assert interface.utterances == []

    def test_hotwords_as_input(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        interface.add_hotwords_from_knowledge(
            Knowledge(_wafl_example), count_threshold=1
        )
        expected = ["jane", "name is", "is jane", "says", "says their", "their name"]
        assert interface._listener._hotwords == expected

    def test_sound_file_is_translated_correctly(self):
        f = wave.open(os.path.join(_path, "data/1002.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        listener = WhisperListener("tiny.en")
        result = listener.input_waveform(waveform)
        result = _normalize_utterance(result)
        expected = "DELETE BATTERIES FROM THE GROCERY LIST"
        assert result == expected

    def test_random_sounds_are_excluded(self):
        f = wave.open(os.path.join(_path, "data/random_sounds.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        listener = WhisperListener("tiny.en")
        result = listener.input_waveform(waveform)
        expected = ""
        assert result == expected

    def test_voice_interface_receives_config(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        assert interface.listener_model_name == config.get_value("listener_model")

    def test__hotword_listener_activated_using_recording_of_hotword(self):
        f = wave.open(os.path.join(_path, "data/computer.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        listener = WhisperListener("tiny.en")
        listener.input_waveform(waveform)
        result = listener.hotword_is_present("computer")

        assert result

    def test__hotword_listener_is_not_activated_using_recording_of_not_hotword(self):
        f = wave.open(os.path.join(_path, "data/1002.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        listener = WhisperListener("tiny.en")
        listener.input_waveform(waveform)
        result = listener.hotword_is_present("computer")

        assert not result


def _normalize_utterance(text):
    text = text.upper()
    for item in [".", ",", "!", ":", ";", "?"]:
        text = text.replace(item, " ")

    text = text.replace("  ", " ")
    return text.strip()
