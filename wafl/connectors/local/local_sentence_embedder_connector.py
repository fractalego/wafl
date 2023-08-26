import torch.cuda
from sentence_transformers import SentenceTransformer
from typing import Dict, List

_device = "cuda" if torch.cuda.is_available() else "cpu"

models_dict = {}

class LocalSentenceEmbedderConnector:
    _max_tries = 3

    def __init__(self, model_name):
        self._model_name = model_name

        global models_dict
        if model_name not in models_dict:
            models_dict[model_name] = SentenceTransformer(model_name, device=_device)

    async def predict(self, text: str) -> Dict[str, List[float]]:
        vector = models_dict[self._model_name].encode(text, show_progress_bar=False)
        return {"embedding": vector}
