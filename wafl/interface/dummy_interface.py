from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.interface import BaseInterface


class DummyInterface(BaseInterface):
    def __init__(self, to_utter=None):
        self.utterances = []
        self._to_utter = to_utter

    def output(self, text: str):
        print("bot>", text)
        self.utterances.append(from_bot_to_user(text))

    def input(self) -> str:
        inp = from_user_to_bot(self._to_utter.pop(0))
        print("user>", inp)
        return inp
