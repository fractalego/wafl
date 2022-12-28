import os
import torch
import numpy as np

from typing import List, Tuple
from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer

from wafl.retriever.base_retriever import BaseRetriever

_path = os.path.dirname(__file__)

device = "cuda" if torch.cuda.is_available() else "cpu"
_sentence_transfomers_dict = {
    "msmarco-distilbert-base-v3": SentenceTransformer(
        "msmarco-distilbert-base-v3", device=device
    ),
    "multi-qa-distilbert-dot-v1": SentenceTransformer(
        "multi-qa-distilbert-dot-v1", device=device
    ),
}


class DenseRetriever(BaseRetriever):
    _threshold_length = 5

    def __init__(self, model_name):
        self._sentence_model = _sentence_transfomers_dict[model_name]
        self._embeddings_model = KeyedVectors(768)

    def add_text_and_index(self, text: str, index: str):
        embeddings = self._get_embeddings_from_text(text)
        self._embeddings_model.add_vectors([index], [embeddings])
        self._embeddings_model.fill_norms(force=True)

    def get_indices_and_scores_from_text(self, text: str) -> List[Tuple[str, float]]:
        if not text or len(text) < self._threshold_length:
            return []

        embeddings = self._get_embeddings_from_text(text)
        return self._embeddings_model.similar_by_vector(embeddings, topn=2)

    def _get_embeddings_from_text(self, text: str) -> "numpy.array":
        return self._sentence_model.encode(text, show_progress_bar=False)

    def get_dot_product(self, lhs: str, rhs: str) -> float:
        lhs_vector = self._sentence_model.encode(lhs, show_progress_bar=False)
        rhs_vector = self._sentence_model.encode(rhs, show_progress_bar=False)
        return (
            np.dot(lhs_vector, rhs_vector)
            / np.linalg.norm(lhs_vector)
            / np.linalg.norm(rhs_vector)
        )
