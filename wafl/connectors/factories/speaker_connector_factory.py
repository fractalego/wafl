from wafl.config import Configuration
from wafl.connectors.remote.remote_speaker_connector import RemoteSpeakerConnector


class SpeakerConnectorFactory:
    @staticmethod
    def get_connector(config: Configuration):
        return RemoteSpeakerConnector(config)
