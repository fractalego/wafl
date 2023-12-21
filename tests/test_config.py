from unittest import TestCase
from wafl.config import Configuration
from wafl.interface.voice_interface import VoiceInterface

_wafl_greetings = """
  
""".strip()


class TestConfig(TestCase):
    def test__listener_accepts_threshold_for_hotword_logp(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        self.assertEqual(
            interface._listener._hotword_threshold,
            config.get_value("listener_model")["listener_hotword_logp"],
        )

    def test__listener_accepts_threshold_for_volume(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        self.assertEqual(
            interface._listener._volume_threshold,
            config.get_value("listener_model")["listener_volume_threshold"],
        )

    def test__listener_accepts_silence_timeout(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        self.assertEqual(
            interface._listener._timeout,
            config.get_value("listener_model")["listener_silence_timeout"],
        )
