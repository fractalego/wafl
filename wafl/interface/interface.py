class BaseInterface:
    def output(self, text: str):
        raise NotImplemented

    def input(self) -> str:
        raise NotImplemented

    def bot_has_spoken(self, to_set: bool = None):
        raise NotImplemented

    def check_understanding(self, do_the_check: bool):
        raise NotImplemented
