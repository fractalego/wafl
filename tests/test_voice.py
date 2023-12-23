import asyncio
import os
import wave
import numpy as np

from unittest import TestCase
from wafl.config import Configuration
from wafl.interface.voice_interface import VoiceInterface
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.listener.whisper_listener import WhisperListener

_wafl_example = """
facts:
  - This bot is doing well
  
rules:
  - the user's name is Jane:
    - write "I hear you"
""".strip()

_path = os.path.dirname(__file__)


class TestVoice(TestCase):
    def test__activation(self):
        interface = DummyInterface(to_utter=["computer", "my name is Jane"])
        config = Configuration.load_local_config()
        config.set_value("rules", _wafl_example)
        conversation_events = ConversationEvents(config=config, interface=interface)
        interface.activate()
        asyncio.run(conversation_events.process_next(activation_word="computer"))
        asyncio.run(conversation_events.process_next(activation_word="computer"))
        assert interface.get_utterances_list()[-1] == "bot: I hear you"

    def test__no_activation(self):
        interface = DummyInterface(to_utter=["my name is bob"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(config=config, interface=interface)
        interface.deactivate()
        asyncio.run(conversation_events.process_next(activation_word="computer"))
        assert len(interface.get_utterances_list()) == 1

    def test__computer_name_is_removed_after_activation(self):
        interface = DummyInterface(to_utter=["[computer] computer my name is bob"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(config=config, interface=interface)
        interface.deactivate()
        asyncio.run(conversation_events.process_next(activation_word="computer"))
        assert interface.get_utterances_list()[-1].count("computer") == 0

    def test__sound_file_is_translated_correctly(self):
        f = wave.open(os.path.join(_path, "data/1002.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        config = Configuration.load_local_config()
        listener = WhisperListener(config)
        result = asyncio.run(listener.input_waveform(waveform))
        result = _normalize_utterance(result)
        expected = "DELETE BATTERIES FROM THE GROCERY LIST"
        assert result == expected

    def test__random_sounds_are_excluded(self):
        f = wave.open(os.path.join(_path, "data/random_sounds.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        config = Configuration.load_local_config()
        listener = WhisperListener(config)
        result = asyncio.run(listener.input_waveform(waveform))
        expected = "[unclear]"
        assert result == expected

    def test__hotword_listener_activated_using_recording_of_hotword(self):
        f = wave.open(os.path.join(_path, "data/computer.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        config = Configuration.load_local_config()
        listener = WhisperListener(config)
        asyncio.run(listener.input_waveform(waveform))
        result = asyncio.run(listener.hotword_is_present("computer"))
        assert result

    def test__hotword_listener_is_not_activated_using_recording_of_not_hotword(self):
        f = wave.open(os.path.join(_path, "data/1002.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        config = Configuration.load_local_config()
        listener = WhisperListener(config)
        asyncio.run(listener.input_waveform(waveform))
        result = asyncio.run(listener.hotword_is_present("computer"))
        assert not result


def _normalize_utterance(text):
    text = text.upper()
    for item in [".", ",", "!", ":", ";", "?"]:
        text = text.replace(item, " ")

    text = text.replace("  ", " ")
    return text.strip()
