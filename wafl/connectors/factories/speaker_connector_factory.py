from wafl.connectors.local.local_speaker_connector import LocalSpeakerConnector
from wafl.connectors.remote.remote_speaker_connector import RemoteSpeakerConnector


class SpeakerConnectorFactory:
    @staticmethod
    def get_connector(config):
        if config.get_value("speaker_model")["model_is_local"]:
            return LocalSpeakerConnector(config.get_value("speaker_model"))

        return RemoteSpeakerConnector(config.get_value("speaker_model")["remote_model"])
