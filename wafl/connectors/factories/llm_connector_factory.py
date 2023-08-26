from wafl.connectors.local.local_llm_connector import LocalLLMConnector
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector


class LLMConnectorFactory:
    @staticmethod
    def get_connector(config):
        if config.get_value("llm_model")["model_is_local"]:
            return LocalLLMConnector(config.get_value("llm_model"))

        return RemoteLLMConnector(config.get_value("llm_model"))
