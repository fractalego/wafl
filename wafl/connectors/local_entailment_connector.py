import torch

from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification
from typing import Dict

device = "cuda" if torch.cuda.is_available() else "cpu"


class LocalEntailmentConnector:
    def __init__(self, config):
        global model, tokenizer
        model_name = config.get_value("entailment_model")["local_model"]
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        model.to(device)
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
