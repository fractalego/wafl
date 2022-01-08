from unittest import TestCase

from wafl.interface.voice_interface import VoiceInterface

from wafl.config import Configuration
from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge

_wafl_greetings = """
  
""".strip()


class TestConfig(TestCase):
    def test_random_facts_are_not_accepted(self):
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

    def test_voice_interface_receives_config(self):
        config = Configuration.load_local_config()
        interface = VoiceInterface(config)
        assert interface.listener_model_name == config.get_value("listener_model")
