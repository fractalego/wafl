import logging
import os

from wafl.connectors.gptj_prompt_predictor_connector import GPTJPromptPredictorConnector
from wafl.extractors.dataclasses import Answer

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class PromptPredictor:
    def __init__(self, logger=None):
        self._model = GPTJPromptPredictorConnector()

    def predict(self, prompt: str):
        return Answer(text=self._model.predict(prompt).strip())
