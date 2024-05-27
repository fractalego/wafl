import re
import time

from wafl.interface.conversation import Utterance
from wafl.simple_text_processing.deixis import from_bot_to_user
from wafl.interface.base_interface import BaseInterface
from wafl.interface.utils import not_good_enough

COLOR_START = "\033[94m"
COLOR_END = "\033[0m"


class DummyInterface(BaseInterface):
    def __init__(self, to_utter=None, print_utterances=False):
        super().__init__()
        self._to_utter = to_utter
        self._bot_has_spoken = False
        self._dialogue = ""
        self._print_utterances = print_utterances

    async def output(self, text: str, silent: bool = False):
        if self._print_utterances:
            if silent:
                print(text)

            else:
                print(COLOR_START + "bot> " + text + COLOR_END)

        if not silent:
            self._dialogue += "bot: " + text + "\n"
            self._insert_utterance(speaker="bot", text=text)
            self.bot_has_spoken(True)

    async def input(self) -> str:
        text = self._to_utter.pop(0).strip()
        text = self.__remove_activation_word_and_normalize(text)
        if self._print_utterances:
            print(COLOR_START + "user> " + text + COLOR_END)

        while self._is_listening and not_good_enough(text):
            await self.output("I did not quite understand that")
            text = self._to_utter.pop(0)

        self._dialogue += "user: " + text + "\n"
        utterance = text
        self._insert_utterance(speaker="user", text=text)
        return utterance

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken

    def get_dialogue(self):
        return self._dialogue

    def __remove_activation_word_and_normalize(self, text):
        activation_word = re.sub(r"\[(.*)\].*", r"\1", text)
        text = re.sub(
            f"^\[{activation_word}\] {activation_word} (.*)",
            r"\1",
            text,
            flags=re.IGNORECASE,
        )
        return text
