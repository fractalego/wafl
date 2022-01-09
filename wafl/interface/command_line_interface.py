from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.interface import BaseInterface
from wafl.interface.utils import not_good_enough


class CommandLineInterface(BaseInterface):
    def __init__(self):
        self._bot_has_spoken = False
        self._check_understanding = True

    def output(self, text: str):
        print("bot>", from_bot_to_user(text))
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

    def check_understanding(self, do_the_check: bool):
        self._check_understanding = do_the_check
