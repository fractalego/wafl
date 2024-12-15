import asyncio
import os

from unittest import TestCase
from wafl.config import Configuration
from wafl.connectors.remote.remote_entailer_connector import RemoteEntailerConnector
from wafl.connectors.clients.entailer_client import EntailerClient

_path = os.path.dirname(__file__)


class TestConnection(TestCase):
    def test__entailer_connector(self):
        config = Configuration.load_local_config()
        connector = RemoteEntailerConnector(config)
        prediction = asyncio.run(
            connector.predict(
                "The first contact is a romance novel set in the middle ages.",
                "The first contact is a science fiction novel about the first contact between humans and aliens.",
            )
        )
        assert prediction["score"] < 0.5

    def test__entailment_client(self):

        config = Configuration.load_local_config()
        client = EntailerClient(config)
        prediction = asyncio.run(
            client.get_entailment_score(
                "The first contact is a romance novel set in the middle ages.",
                "The first contact is a science fiction novel about the first contact between humans and aliens.",
            )
        )
        assert prediction < 0.5
