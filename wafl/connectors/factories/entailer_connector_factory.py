from wafl.config import Configuration
from wafl.connectors.remote.remote_entailer_connector import RemoteEntailerConnector


class EntailerConnectorFactory:
    @staticmethod
    def get_connector(config: Configuration):
        return RemoteEntailerConnector(config)
