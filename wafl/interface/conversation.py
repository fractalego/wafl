from dataclasses import dataclass
from typing import List


@dataclass
class Utterance:
    text: str
    speaker: str
    timestamp: str

    def to_dict(self):
        return {"text": self.text, "speaker": self.speaker, "timestamp": self.timestamp}


@dataclass
class Conversation:
    utterances: List[Utterance] = None

    def to_dict(self):
        return {"utterances": [utterance.to_dict() for utterance in self.utterances]}
