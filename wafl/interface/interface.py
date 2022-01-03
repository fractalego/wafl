class BaseInterface:
    def output(self, text: str):
        raise NotImplemented("Interface.output() needs to be implemented")

    def input(self) -> str:
        raise NotImplemented("Interface.input() needs to be implemented")
