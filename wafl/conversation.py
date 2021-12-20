from dataclasses import dataclass


@dataclass
class Utterance:
    speaker: str
    text: str
    timestamp: int
    is_question: bool = False

    def __str__(self):
        return self.text


class Conversation:
    def __init__(self, knowledge):
        self._knowledge = knowledge
        self._utterances = []
        self._to_utter = []
        self._timestamp = 0

    def utter(self, text):
        self._to_utter.append(
            Utterance(speaker="BOT", utterance=text, timestamp=self._timestamp)
        )
        self._timestamp += 1

    def next(self):
        utterance = self._to_utter.pop()
        self._utterances.append(utterance)
        return utterance

    def answer(self, text):
        self._utterances.append(
            Utterance(speaker="USER", utterance=text, timestamp=self._timestamp)
        )
        self._timestamp += 1
