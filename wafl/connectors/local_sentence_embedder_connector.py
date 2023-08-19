from typing import Dict, List
from sentence_transformers import SentenceTransformer


class LocalSentenceEmbedderConnector:
    _max_tries = 3

    def __init__(self, model_name):
        self._model = SentenceTransformer(model_name, device="cuda")

    async def predict(self, text: str) -> Dict[str, List[float]]:
        vector = self._model.encode(text, show_progress_bar=False)
        return {"embedding": vector}
