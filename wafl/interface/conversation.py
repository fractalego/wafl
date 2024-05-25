from dataclasses import dataclass
from datetime import datetime
from typing import List


@dataclass
class Utterance:
    text: str
    speaker: str
    timestamp: float

    def __init__(self, text: str, speaker: str, timestamp: float = None):
        self.text = text
        self.speaker = speaker
        self.timestamp = timestamp
        if self.timestamp is None:
            self.timestamp = datetime.now().timestamp()

    def to_dict(self):
        return {"text": self.text, "speaker": self.speaker, "timestamp": self.timestamp}


@dataclass
class Conversation:
    utterances: List[Utterance] = None

    def __init__(self, utterances: List[Utterance] = None):
        self.utterances = utterances

    def add_utterance(self, utterance: Utterance):
        if self.utterances is None:
            self.utterances = []

        if (
            len(self.utterances) > 0
            and utterance.text == self.utterances[-1].text
            and utterance.speaker == self.utterances[-1].speaker
        ):
            return

        self.utterances.append(utterance)

    def to_dict(self):
        return [utterance.to_dict() for utterance in self.utterances]
