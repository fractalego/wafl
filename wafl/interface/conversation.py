from dataclasses import dataclass
from typing import List


@dataclass
class Utterance:
    text: str
    speaker: str
    timestamp: float

    def to_dict(self):
        return {"text": self.text, "speaker": self.speaker, "timestamp": self.timestamp}


@dataclass
class Conversation:
    utterances: List[Utterance] = None

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
        return {"utterances": [utterance.to_dict() for utterance in self.utterances]}
