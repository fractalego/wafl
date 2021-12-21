class BaseInterface:
    def output(self, text: str):
        raise NotImplemented("Interface.output() needs to be implemented")

    def input(self) -> str:
        raise NotImplemented("Interface.input() needs to be implemented")


class CommandLineInterface(BaseInterface):
    def output(self, text: str):
        print("bot>", text)

    def input(self) -> str:
        return input("user> ")


class DummyInterface(BaseInterface):
    def __init__(self, to_utter=None):
        self.utterances = []
        self._to_utter = to_utter

    def output(self, text: str):
        self.utterances.append(text)

    def input(self) -> str:
        return self._to_utter.pop(0)
