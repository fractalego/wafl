from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.interface import BaseInterface
from wafl.interface.utils import not_good_enough


class CommandLineInterface(BaseInterface):
    def output(self, text: str):
        print("bot>", from_bot_to_user(text))

    def input(self) -> str:
        text = from_user_to_bot(input("user> ")).strip()
        while not_good_enough(text):
            self.output("I did not quite understand that")
            text = from_user_to_bot(input("user> "))
        return text
