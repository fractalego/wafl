import logging
import os

from wafl.connectors.llm_prompt_predictor_connector import LLMPromptPredictorConnector
from wafl.extractors.dataclasses import Answer

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)


class PromptPredictor:
    def __init__(self, config, logger=None):
        self._model = LLMPromptPredictorConnector(config.get_value("llm_model"))
        self._closing_tag = "</result>"

    async def predict(self, prompt: str):
        prediction = await self._model.get_answer(prompt, "", "")
        prediction = prediction.replace(self._closing_tag, "").strip()
        return Answer(text=prediction.strip())
