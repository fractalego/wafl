import os

from wafl.connectors.factories.entailer_connector_factory import (
    EntailerConnectorFactory,
)

_path = os.path.dirname(__file__)


class EntailerClient:
    def __init__(self, config):
        self._connector = EntailerConnectorFactory.get_connector(config)
        self._config = config

    async def get_entailment_score(self, lhs: str, rhs: str) -> float:
        prediction = await self._connector.predict(lhs, rhs)
        if "score" not in prediction:
            raise ValueError("The Entailment prediction does not contain a score.")
        return prediction["score"]
