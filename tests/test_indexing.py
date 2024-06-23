import os
import yaml

from unittest import TestCase
from wafl.knowledge.indexing_implementation import add_to_index

_path = os.path.dirname(__file__)



class TestIndexing(TestCase):
    def test__path_can_be_added_to_index(self):
        data = _load_index()
        prior_count = len(data["paths"])
        add_to_index("files_to_index")

        data = _load_index()
        current_count = len(data["paths"])
        self.assertEqual(current_count, prior_count + 1)

        data["paths"].remove("files_to_index")
        with open("indices.yaml", "w") as file:
            file.write(yaml.dump(data))



def _load_index():
    with open("indices.yaml", "r") as file:
        return yaml.safe_load(file.read())