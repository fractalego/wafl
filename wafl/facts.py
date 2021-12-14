from dataclasses import dataclass

@dataclass
class Fact:
    text: str

    def toJSON(self):
        return str(self)
