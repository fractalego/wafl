from wafl.deixis import from_bot_to_user, from_user_to_bot
from wafl.interface.base_interface import BaseInterface
from wafl.interface.utils import not_good_enough


class DummyInterface(BaseInterface):
    def __init__(self, to_utter=None):
        self.utterances = []
        self._to_utter = to_utter
        self._bot_has_spoken = False
        self._dialogue = ""
        self._check_understanding = True

    def output(self, text: str):
        self._dialogue += "bot> " + text + "\n"
        self.utterances.append(from_bot_to_user(text))
        self.bot_has_spoken(True)

    def input(self) -> str:
        text = self._to_utter.pop(0).strip()
        while self._check_understanding and not_good_enough(text):
            self.output("I did not quite understand that")
            text = from_user_to_bot(self._to_utter.pop(0))
        self._dialogue += "user> " + text + "\n"
        return from_user_to_bot(text)

    def bot_has_spoken(self, to_set: bool = None):
        if to_set != None:
            self._bot_has_spoken = to_set

        return self._bot_has_spoken

    def get_dialogue(self):
        return self._dialogue

    def check_understanding(self, do_the_check: bool = None):
        if do_the_check == None:
            return self._check_understanding

        self._check_understanding = do_the_check
