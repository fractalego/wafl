import logging

import torch

from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from typing import Dict

_system_logger = logging.getLogger(__file__)

device = "cuda" if torch.cuda.is_available() else "cpu"

model = None
tokenizer = None


class LocalEntailmentConnector:
    def __init__(self, config):
        global model, tokenizer
        if not model:
            model_name = config["local_model"]
            _system_logger.info(f"Loading model {model_name} locally.")
            model = AutoModelForSequenceClassification.from_pretrained(model_name)
            model.to(device)
            _system_logger.info(f"The model is loaded.")

        if not tokenizer:
            tokenizer = AutoTokenizer.from_pretrained(model_name)

        self._cache = {}

    async def predict(self, premise: str, hypothesis: str) -> Dict[str, float]:
        input_ids = tokenizer(
            premise, hypothesis, truncation=True, return_tensors="pt"
        ).input_ids.to(device)
        output = model(input_ids)
        prediction = torch.softmax(output["logits"], -1)[0]
        label_names = ["entailment", "neutral", "contradiction"]
        answer = {name: float(pred) for pred, name in zip(prediction, label_names)}
        return answer
