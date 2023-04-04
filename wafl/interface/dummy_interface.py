import time

from wafl.simple_text_processing.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.base_interface import BaseInterface
from wafl.interface.utils import not_good_enough


class DummyInterface(BaseInterface):
    def __init__(self, to_utter=None):
        super().__init__()
        self._to_utter = to_utter
        self._bot_has_spoken = False
        self._dialogue = ""

    def output(self, text: str, silent: bool = False):
        if silent:
            print(text)
            return

        self._dialogue += "bot: " + text + "\n"
        self._utterances.append((time.time(), f"bot: {from_bot_to_user(text)}"))
        self.bot_has_spoken(True)

    async def input(self) -> str:
        text = self._to_utter.pop(0).strip()
        while self._is_listening and not_good_enough(text):
            self.output("I did not quite understand that")
            text = from_user_to_bot(self._to_utter.pop(0))

        self._dialogue += "user: " + text + "\n"
        utterance = from_user_to_bot(text)
        self._utterances.append((time.time(), f"user: {utterance}"))
        return utterance

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken

    def get_dialogue(self):
        return self._dialogue
