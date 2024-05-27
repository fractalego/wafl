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

    def __str__(self):
        return f"{self.speaker}: {self.text}"


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

        if (
            len(self.utterances) > 0
            and utterance.speaker == self.utterances[-1].speaker
        ):
            self.utterances[-1].text += "\n" + utterance.text
            return

        self.utterances.append(utterance)
        self.utterances = sorted(self.utterances, key=lambda x: x.timestamp)

    def insert_utterance(self, new_utterance: Utterance):
        """
        Insert a new utterance into the conversation at the timestamp defined in the utterance.
        :param new_utterance:
        """
        if self.utterances is None:
            self.utterances = []

        new_utterances = []
        already_inserted = False
        for utterance in self.utterances:
            if (
                not already_inserted
                and utterance.speaker == new_utterance.speaker
                and utterance.timestamp == new_utterance.timestamp
            ):
                new_utterances.append(
                    Utterance(
                        new_utterance.text,
                        new_utterance.speaker,
                        new_utterance.timestamp,
                    )
                )
                already_inserted = True

            new_utterances.append(
                Utterance(utterance.text, utterance.speaker, utterance.timestamp)
            )

        self.utterances = new_utterances

    def get_last_n(self, n: int) -> "Conversation":
        return Conversation(self.utterances[-n:]) if self.utterances else Conversation()

    def get_last_speaker_utterances(self, speaker: str, n: int) -> List[str]:
        if not self.utterances:
            return []

        return [
            utterance.text
            for utterance in self.utterances
            if utterance.speaker == speaker
        ][-n:]

    def get_first_timestamp(self) -> float:
        return self.utterances[0].timestamp if self.utterances else None

    def get_last_timestamp(self) -> float:
        return self.utterances[-1].timestamp if self.utterances else None

    def to_dict(self):
        return [utterance.to_dict() for utterance in self.utterances]

    def get_utterances_list(self) -> List[Utterance]:
        if not self.utterances:
            return []
        return self.utterances

    def __len__(self):
        if not self.utterances:
            return 0
        return len(self.utterances)
