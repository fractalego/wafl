class BaseInterface:
    def output(self, text: str):
        raise NotImplementedError

    def input(self) -> str:
        raise NotImplementedError

    def bot_has_spoken(self, to_set: bool = None):
        raise NotImplementedError

    def check_understanding(self, do_the_check: bool):
        raise NotImplementedError

    def get_utterances_list(self):
        raise NotImplementedError
