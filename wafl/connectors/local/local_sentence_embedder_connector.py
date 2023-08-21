import torch.cuda
from sentence_transformers import SentenceTransformer
from typing import Dict, List

_device = "cuda" if torch.cuda.is_available() else "cpu"


class LocalSentenceEmbedderConnector:
    _max_tries = 3

    def __init__(self, model_name):
        self._model = SentenceTransformer(model_name, device=_device)

    async def predict(self, text: str) -> Dict[str, List[float]]:
        vector = self._model.encode(text, show_progress_bar=False)
        return {"embedding": vector}
