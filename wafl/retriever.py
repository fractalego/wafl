import os
import torch
import logging

from gensim.models import KeyedVectors
from sentence_transformers import SentenceTransformer

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
sentence_model = SentenceTransformer('msmarco-distilbert-base-v3')
sentence_model = sentence_model.to(device)


class Retriever:
    _embeddings_model = KeyedVectors(768)

    def add_text_and_index(self, text, index):
        embeddings = _get_embeddings_from_text(text)
        self._embeddings_model.add_vector(index, embeddings)

    def get_indices_and_scores_from_text(self, text):
        embeddings = _get_embeddings_from_text(text)
        return self._embeddings_model.similar_by_vector(embeddings, topn=2)


def _get_embeddings_from_text(text):
    return sentence_model.encode(text)
