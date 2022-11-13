from unittest import TestCase

from wafl.config import Configuration
from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_greetings = """
  
""".strip()


class TestConfig(TestCase):
    def test__random_facts_are_not_accepted(self):
        config = Configuration.load_local_config()
        config.set_value("accept_random_facts", False)

        interface = DummyInterface(["My name is Albert", "What is my name"])
        conversation = Conversation(
            Knowledge(_wafl_greetings), interface=interface, config=config
        )
        utterance = "Welcome to the website. How may I help you?"
        conversation.output(utterance)
        conversation.input()
        conversation.input()
        assert interface.utterances[-1] == "Unknown"

    def test__listener_accepts_threshold_for_hotword_logp(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        self.assertEqual(
            interface._listener._hotword_threshold,
            config.get_value("listener_hotword_logp"),
        )

    def test__listener_accepts_threshold_for_volume(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        self.assertEqual(
            interface._listener._volume_threshold,
            config.get_value("listener_volume_threshold"),
        )

    def test__listener_accepts_silence_timeout(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        self.assertEqual(
            interface._listener._timeout, config.get_value("listener_silence_timeout")
        )
