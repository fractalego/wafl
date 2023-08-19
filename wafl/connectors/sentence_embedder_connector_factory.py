from wafl.connectors.local_sentence_embedder_connector import (
    LocalSentenceEmbedderConnector,
)


class SentenceEmbedderConnectorFactory:
    @staticmethod
    def get_connector(model_name, config):
        if config.get_value(model_name)["model_is_local"]:
            return LocalSentenceEmbedderConnector(
                config.get_value(model_name)["local_model"]
            )
