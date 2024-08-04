import asyncio
import os
import yaml

from unittest import TestCase

from wafl.config import Configuration
from wafl.data_objects.dataclasses import Query
from wafl.knowledge.indexing_implementation import add_to_index, load_knowledge

_path = os.path.dirname(__file__)


class TestIndexing(TestCase):
    def test__path_can_be_added_to_index(self):
        data = _load_index()
        prior_count = len(data["paths"])
        add_to_index("files_to_index2")

        data = _load_index()
        current_count = len(data["paths"])
        self.assertEqual(current_count, prior_count + 1)

        data["paths"].remove("files_to_index2")
        with open("indices.yaml", "w") as file:
            file.write(yaml.dump(data))

    def test__indexed_files_can_be_retrieved(self):
        config = Configuration.load_local_config()
        knowledge = asyncio.run(load_knowledge(config))
        results = asyncio.run(
            knowledge.ask_for_facts(Query.create_from_text("How do I start WAFL"))
        )
        expected = "WAFL"
        self.assertIn(expected, results[0].text)

    def test__pdf_can_be_read(self):
        config = Configuration.load_local_config()
        knowledge = asyncio.run(load_knowledge(config))
        results = asyncio.run(
            knowledge.ask_for_facts(Query.create_from_text("What color is the sky?"))
        )
        expected = "green"
        self.assertIn(expected, results[0].text)


def _load_index():
    with open("indices.yaml", "r") as file:
        return yaml.safe_load(file.read())
