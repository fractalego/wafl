from dataclasses import dataclass

from wafl.inference import BackwardInference


@dataclass
class Utterance:
    speaker: str
    text: str
    timestamp: int
    is_question: bool = False

    def __str__(self):
        return self.text


class Conversation:
    def __init__(self, knowledge, interface):
        self._knowledge = knowledge
        self._interface = interface
        self._inference = BackwardInference(knowledge, interface)

    def utter(self, text):
        self._interface.output(text)
