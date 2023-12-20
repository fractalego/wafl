import time

from wafl.simple_text_processing.deixis import from_bot_to_user
from wafl.interface.base_interface import BaseInterface
from wafl.interface.utils import not_good_enough

COLOR_START = "\033[94m"
COLOR_END = "\033[0m"


class CommandLineInterface(BaseInterface):
    def __init__(self):
        super().__init__()
        self._bot_has_spoken = False

    async def output(self, text: str, silent: bool = False):
        if silent:
            print(text)
            return

        utterance = from_bot_to_user(text)
        print(COLOR_START + "bot> " + utterance + COLOR_END)
        self._utterances.append((time.time(), f"bot: {text}"))
        self.bot_has_spoken(True)

    async def input(self) -> str:
        text = input("user> ").strip()
        while not_good_enough(text):
            await self.output("I did not quite understand that")
            text = input("user> ")

        self._utterances.append((time.time(), f"user: {text}"))
        return text

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken
