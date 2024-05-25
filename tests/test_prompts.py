import os
from unittest import TestCase

from wafl.interface.conversation import Conversation, Utterance
from wafl.connectors.prompt_template import PrompCreator

_path = os.path.dirname(__file__)


class TestPrompts(TestCase):
    def test_utterance(self):
        utterance = Utterance(
            text="Hello", speaker="user", timestamp="2022-01-01T00:00:00"
        )
        self.assertEqual(
            utterance.to_dict(),
            {"text": "Hello", "speaker": "user", "timestamp": "2022-01-01T00:00:00"},
        )

    def test_conversation(self):
        utterance1 = Utterance(
            text="Hello", speaker="user", timestamp="2022-01-01T00:00:00"
        )
        utterance2 = Utterance(
            text="Hi", speaker="bot", timestamp="2022-01-01T00:00:01"
        )
        conversation = Conversation(utterances=[utterance1, utterance2])
        self.assertEqual(
            conversation.to_dict(),
            {
                "utterances": [
                    {
                        "text": "Hello",
                        "speaker": "user",
                        "timestamp": "2022-01-01T00:00:00",
                    },
                    {
                        "text": "Hi",
                        "speaker": "bot",
                        "timestamp": "2022-01-01T00:00:01",
                    },
                ]
            },
        )

    def test_prompt(self):
        utterance1 = Utterance(
            text="Hello", speaker="user", timestamp="2022-01-01T00:00:00"
        )
        utterance2 = Utterance(
            text="Hi", speaker="bot", timestamp="2022-01-01T00:00:01"
        )
        conversation = Conversation(utterances=[utterance1, utterance2])
        prompt = PrompCreator.create(system_prompt="Hello", conversation=conversation)
        self.assertEqual(
            prompt.to_dict(),
            {
                "system_prompt": "Hello",
                "conversation": {
                    "utterances": [
                        {
                            "text": "Hello",
                            "speaker": "user",
                            "timestamp": "2022-01-01T00:00:00",
                        },
                        {
                            "text": "Hi",
                            "speaker": "bot",
                            "timestamp": "2022-01-01T00:00:01",
                        },
                    ]
                },
            },
        )
