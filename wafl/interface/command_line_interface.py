from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.interface import BaseInterface
from wafl.interface.utils import not_good_enough

COLOR_START = "\033[94m"
COLOR_END = "\033[0m"


class CommandLineInterface(BaseInterface):
    def __init__(self):
        self._bot_has_spoken = False
        self._check_understanding = True

    def output(self, text: str):
        print(COLOR_START + "bot> " + from_bot_to_user(text) + COLOR_END)
        self.bot_has_spoken(True)

    def input(self) -> str:
        text = from_user_to_bot(input("user> ")).strip()
        while self._check_understanding and not_good_enough(text):
            self.output("I did not quite understand that")
            text = from_user_to_bot(input("user> "))
        return text

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken

    def check_understanding(self, do_the_check: bool = None):
        if do_the_check == None:
            return self._check_understanding

        self._check_understanding = do_the_check
