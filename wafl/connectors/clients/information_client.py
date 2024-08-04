import os

from wafl.connectors.factories.llm_connector_factory import LLMConnectorFactory

_path = os.path.dirname(__file__)


class InformationClient:
    def __init__(self, config):
        self._connector = LLMConnectorFactory.get_connector(config)
        self._config = config

    async def get_information(self) -> str:
        return await self._connector.get_information()
