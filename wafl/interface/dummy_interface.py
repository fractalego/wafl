from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.interface import BaseInterface
from wafl.interface.utils import not_good_enough


class DummyInterface(BaseInterface):
    def __init__(self, to_utter=None):
        self.utterances = []
        self._to_utter = to_utter

    def output(self, text: str):
        print("bot>", text)
        self.utterances.append(from_bot_to_user(text))

    def input(self) -> str:
        text = from_user_to_bot(self._to_utter.pop(0)).strip()
        while not_good_enough(text):
            self.output("I did not quite understand that")
            text = from_user_to_bot(self._to_utter.pop(0))
        text = text.lower().capitalize()
        print("user>", text)
        return from_user_to_bot(text)
