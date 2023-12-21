from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector


class LLMConnectorFactory:
    @staticmethod
    def get_connector(config):
        return RemoteLLMConnector(config.get_value("llm_model"))
