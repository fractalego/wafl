import os
import torch

from typing import Dict, Union
from transformers import AutoTokenizer, AutoModelForSequenceClassification

os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

_model_name = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
_tokenizer = AutoTokenizer.from_pretrained(_model_name)
_model = AutoModelForSequenceClassification.from_pretrained(_model_name).to(_device)


class Entailer:
    def __init__(self, logger=None):
        self._tokenizer = _tokenizer
        self._model = _model
        if torch.cuda.is_available():
            self._model.half()

        self._logger = logger

    def get_relation(self, premise: str, hypothesis: str) -> Dict[str, float]:
        encodings = self._tokenizer(
            premise, hypothesis, truncation=True, return_tensors="pt"
        )
        output = self._model(encodings["input_ids"].to(_device))
        prediction = torch.softmax(output["logits"][0], -1).tolist()
        label_names = ["entailment", "neutral", "contradiction"]
        prediction = {name: float(pred) for pred, name in zip(prediction, label_names)}
        return prediction

    def entails(
        self,
        premise: str,
        hypothesis: str,
        threshold=0.75,
        contradiction_threshold=0.65,
        return_threshold=False,
    ) -> Union[str, float]:
        if self._logger:
            self._logger.write("Starting entailment procedure.")

        prediction = self.get_relation(premise, hypothesis)
        if prediction["entailment"] > threshold:
            if self._logger:
                self._logger.write(f"Entailment: The premise is {premise}")
                self._logger.write(f"Entailment: The hypothesis is {hypothesis}")
                self._logger.write(f"Entailment: The results are {str(prediction)}")

            if return_threshold:
                return prediction["entailment"]

            return "True"

        if prediction["contradiction"] < contradiction_threshold:
            premise = self._add_presuppositions_to_premise(premise)
            prediction = self.get_relation(premise, hypothesis)

        if self._logger:
            self._logger.write(f"Entailment: The premise is {premise}")
            self._logger.write(f"Entailment: The hypothesis is {hypothesis}")
            self._logger.write(f"Entailment: The results are {str(prediction)}")

        if prediction["entailment"] > threshold:
            if return_threshold:
                return prediction["entailment"]

            return "True"

        if return_threshold:
            return 0

        if prediction["neutral"] > threshold:
            return "Unknown"

        return "False"

    def is_neutral(
        self,
        premise: str,
        hypothesis: str,
        threshold=0.75,
    ) -> Union[str, float]:
        if self._logger:
            self._logger.write("Starting entailment neutral check.")

        prediction = self.get_relation(premise, hypothesis)
        if prediction["neutral"] > threshold:
            if self._logger:
                self._logger.write(f"Entailment: The premise is {premise}")
                self._logger.write(f"Entailment: The hypothesis is {hypothesis}")
                self._logger.write(f"Entailment: The results are {str(prediction)}")

            return True

        if self._logger:
            self._logger.write(f"Entailment: The premise is {premise}")
            self._logger.write(f"Entailment: The hypothesis is {hypothesis}")
            self._logger.write(f"Entailment: The results are {str(prediction)}")

        if prediction["neutral"] > threshold:
            return True

        return False

    def _add_presuppositions_to_premise(self, premise):
        premise = premise.replace("user says:", "user says to this bot:")
        premise = premise.replace("user asks:", "user asks to this bot:")
        return premise