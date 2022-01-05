import os
import torch
import logging
import numpy as np

from typing import List, Tuple
from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer

from wafl.retriever.base_retriever import BaseRetriever

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sentence_model = SentenceTransformer("msmarco-distilbert-base-v3")
sentence_model = sentence_model.to(device)


class TextRetriever(BaseRetriever):
    def __init__(self):
        self._embeddings_model = KeyedVectors(768)

    def add_text_and_index(self, text: str, index: str):
        embeddings = _get_embeddings_from_text(text)
        self._embeddings_model.add_vector(index, embeddings)
        self._embeddings_model.fill_norms(force=True)

    def get_indices_and_scores_from_text(self, text: str) -> List[Tuple[str, float]]:
        if not text:
            return []

        embeddings = _get_embeddings_from_text(text)
        return self._embeddings_model.similar_by_vector(embeddings, topn=2)


def _get_embeddings_from_text(text: str) -> "numpy.array":
    return sentence_model.encode(text)


def get_dot_product(lhs: str, rhs: str) -> float:
    lhs_vector = sentence_model.encode(lhs)
    rhs_vector = sentence_model.encode(rhs)
    return (
        np.dot(lhs_vector, rhs_vector)
        / np.linalg.norm(lhs_vector)
        / np.linalg.norm(rhs_vector)
    )
