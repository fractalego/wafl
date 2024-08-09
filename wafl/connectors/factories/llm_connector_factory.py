from wafl.config import Configuration
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector


class LLMConnectorFactory:
    @staticmethod
    def get_connector(config: Configuration):
        return RemoteLLMConnector(config)
