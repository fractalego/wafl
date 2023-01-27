from typing import List


class BaseInterface:
    def __init__(self):
        self._is_listening = True

    def output(self, text: str):
        raise NotImplementedError

    def input(self) -> str:
        raise NotImplementedError

    def bot_has_spoken(self, to_set: bool = None):
        raise NotImplementedError

    def is_listening(self):
        return self._is_listening

    def activate(self):
        self._is_listening = True

    def deactivate(self):
        self._is_listening = False

    def get_utterances_list(self):
        raise NotImplementedError

    def add_hotwords(self, hotwords: List[str]):
        pass
