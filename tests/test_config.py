from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_wafl_greetings = """
  
""".strip()


class TestConfig(TestCase):
    def test__random_facts_are_not_accepted(self):
        config = Configuration.load_local_config()
        config.set_value("accept_random_facts", False)

        interface = DummyInterface(["Albert is here", "What is my name"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_greetings), interface=interface, config=config
        )
        utterance = "Welcome to the website. How may I help you?"
        interface.output(utterance)
        conversation_events.process_next()
        conversation_events.process_next()
        assert interface.get_utterances_list()[-1] == "bot: I don't know"

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
