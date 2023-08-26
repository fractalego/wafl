from wafl.connectors.local.local_whisper_connector import LocalWhisperConnector
from wafl.connectors.remote.remote_whisper_connector import RemoteWhisperConnector


class WhisperConnectorFactory:
    @staticmethod
    def get_connector(config):
        if config.get_value("listener_model")["model_is_local"]:
            return LocalWhisperConnector(config.get_value("listener_model"))

        return RemoteWhisperConnector(
            config.get_value("listener_model")["remote_model"]
        )
