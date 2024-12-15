from wafl.config import Configuration
from wafl.connectors.remote.remote_sentence_embedder_connector import (
    RemoteSentenceEmbedderConnector,
)


class SentenceEmbedderConnectorFactory:
    @staticmethod
    def get_connector(config: Configuration):
        return RemoteSentenceEmbedderConnector(config)
