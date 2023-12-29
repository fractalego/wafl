import os
import numpy as np

from typing import List, Tuple
from gensim.models import KeyedVectors
from wafl.connectors.factories.sentence_embedder_connector_factory import (
    SentenceEmbedderConnectorFactory,
)
from wafl.retriever.base_retriever import BaseRetriever

_path = os.path.dirname(__file__)


class DenseRetriever(BaseRetriever):
    _threshold_length = 5

    def __init__(self, model_name, config):
        self._connector = SentenceEmbedderConnectorFactory.get_connector(
            model_name, config
        )
        self._embeddings_model = KeyedVectors(384)

    async def add_text_and_index(self, text: str, index: str):
        embeddings = await self._get_embeddings_from_text(text)
        self._embeddings_model.add_vectors([index], [embeddings])
        self._embeddings_model.fill_norms(force=True)

    async def get_indices_and_scores_from_text(
        self, text: str
    ) -> List[Tuple[str, float]]:
        embeddings = await self._get_embeddings_from_text(text)
        return self._embeddings_model.similar_by_vector(embeddings, topn=5)

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
