from wafl.config import Configuration
from wafl.connectors.remote.remote_whisper_connector import RemoteWhisperConnector


class WhisperConnectorFactory:
    @staticmethod
    def get_connector(config: Configuration):
        return RemoteWhisperConnector(config)
