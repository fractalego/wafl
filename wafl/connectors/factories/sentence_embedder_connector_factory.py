from wafl.connectors.remote.remote_sentence_embedder_connector import (
    RemoteSentenceEmbedderConnector,
)


class SentenceEmbedderConnectorFactory:
    @staticmethod
    def get_connector(model_name, config):
        return RemoteSentenceEmbedderConnector(config.get_value(model_name))
