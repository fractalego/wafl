from creak_sense import CreakSense
from wafl.qa.dataclasses import Answer


class CommonSense:
    def __init__(self):
        self._model = CreakSense("fractalego/creak-sense")

    def claim_makes_sense(self, claim):
        prediction = self._model.make_sense(claim)
        if prediction:
            return Answer(text="True")

        return Answer(text="False")
