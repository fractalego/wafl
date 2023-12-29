from wafl.connectors.remote.remote_whisper_connector import RemoteWhisperConnector


class WhisperConnectorFactory:
    @staticmethod
    def get_connector(config):
        return RemoteWhisperConnector(config.get_value("listener_model"))
