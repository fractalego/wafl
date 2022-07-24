import torch

from typing import Dict
from transformers import AutoTokenizer, AutoModelForSequenceClassification

_device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


class Entailer:
    def __init__(self):
        model_name = "MoritzLaurer/DeBERTa-v3-base-mnli-fever-anli"
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForSequenceClassification.from_pretrained(model_name).to(
            _device
        )

    def get_relation(self, premise: str, hypothesis: str) -> Dict[str, float]:
        encodings = self._tokenizer(
            premise, hypothesis, truncation=True, return_tensors="pt"
        )
        output = self._model(encodings["input_ids"].to(_device))
        prediction = torch.softmax(output["logits"][0], -1).tolist()
        label_names = ["entailment", "neutral", "contradiction"]
        prediction = {name: float(pred) for pred, name in zip(prediction, label_names)}
        return prediction

    def entails(self, premise: str, hypothesis: str, threshold=0.8) -> bool:
        prediction = self.get_relation(premise, hypothesis)
        if prediction["entailment"] > threshold:
            return True

        if prediction["neutral"] > threshold:
            premise = self._add_presuppositions_to_premise(premise)
            prediction = self.get_relation(premise, hypothesis)

        return prediction["entailment"] > threshold

    def _add_presuppositions_to_premise(self, premise):
        premise = premise.replace("user says:", "user says to this bot:")
        premise = premise.replace("user asks:", "user asks to this bot:")
        return premise
