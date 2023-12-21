from wafl.connectors.remote.remote_speaker_connector import RemoteSpeakerConnector


class SpeakerConnectorFactory:
    @staticmethod
    def get_connector(config):
        return RemoteSpeakerConnector(config.get_value("speaker_model"))
