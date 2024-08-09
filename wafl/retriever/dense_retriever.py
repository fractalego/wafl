import os
import numpy as np

from typing import List, Tuple
from wafl.connectors.factories.sentence_embedder_connector_factory import (
    SentenceEmbedderConnectorFactory,
)
from wafl.retriever.base_retriever import BaseRetriever

_path = os.path.dirname(__file__)


class DenseRetriever(BaseRetriever):
    _threshold_length = 5

    def __init__(self, model_name, config):
        self._connector = SentenceEmbedderConnectorFactory.get_connector(config)
        self._matrix = np.zeros((0, 384))
        self._indices = []

    async def add_text_and_index(self, text: str, index: str):
        embeddings = await self._get_embeddings_from_text(text)
        self._matrix = np.vstack([self._matrix, embeddings])
        self._indices.append(index)

    async def get_indices_and_scores_from_text(
        self, text: str, topn: int = 5
    ) -> List[Tuple[str, float]]:
        embeddings = await self._get_embeddings_from_text(text)
        scores = np.dot(self._matrix, embeddings) / (
            np.linalg.norm(self._matrix, axis=1) * np.linalg.norm(embeddings)
        )
        indices_and_scores = list(zip(self._indices, scores))
        indices_and_scores.sort(key=lambda x: x[1], reverse=True)
        return indices_and_scores[:topn]

    async def _get_embeddings_from_text(self, text: str) -> "numpy.array":
        return (await self._connector.predict(text))["embedding"]

    async def get_dot_product(self, lhs: str, rhs: str) -> float:
        lhs_vector = (await self._connector.predict(lhs))["embedding"]
        rhs_vector = (await self._connector.predict(rhs))["embedding"]
        return (
            np.dot(lhs_vector, rhs_vector)
            / np.linalg.norm(lhs_vector)
            / np.linalg.norm(rhs_vector)
        )
