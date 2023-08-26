from wafl.connectors.local.local_entailment_connector import LocalEntailmentConnector
from wafl.connectors.remote.remote_entailment_connector import RemoteEntailmentConnector


class EntailmentConnectorFactory:
    @staticmethod
    def get_connector(config):
        if config.get_value("entailment_model")["model_is_local"]:
            return LocalEntailmentConnector(config.get_value("entailment_model"))

        return RemoteEntailmentConnector(config.get_value("entailment_model"))
