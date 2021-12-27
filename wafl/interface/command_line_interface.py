from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.interface import BaseInterface


class CommandLineInterface(BaseInterface):
    def output(self, text: str):
        print("bot>", from_bot_to_user(text))

    def input(self) -> str:
        return from_user_to_bot(input("user> "))
