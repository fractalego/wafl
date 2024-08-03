from wafl.connectors.remote.remote_entailer_connector import RemoteEntailerConnector


class EntailerConnectorFactory:
    @staticmethod
    def get_connector(model_name, config):
        return RemoteEntailerConnector(config.get_value(model_name))
