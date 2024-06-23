import os

import joblib
import yaml

from wafl.config import Configuration
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.readers.reader_factory import ReaderFactory


def _add_indices_to_knowledge(knowledge, text):
    indices = yaml.safe_load(text)
    for path in indices["paths"]:
        for root, _, files in os.walk(path):
            for file in files:
                with open(os.path.join(root, file)) as f:
                    reader = ReaderFactory.get_reader(file)
                    for chunk in reader.get_chunks(f.read()):
                        knowledge.add(chunk)

    return knowledge


def load_knowledge(config, logger):
    if ".yaml" in config.get_value("rules") and not any(
        item in config.get_value("rules") for item in [" ", "\n"]
    ):
        with open(config.get_value("rules")) as file:
            rules_txt = file.read()

    else:
        rules_txt = config.get_value("rules")

    index_filename = config.get_value("index")
    with open(index_filename) as file:
        index_txt = file.read()

    if os.path.exists(config.get_value("index_filename")):
        knowledge = joblib.load(config.get_value("index_filename"))
        if knowledge.hash == hash(rules_txt + index_txt):
            return knowledge

    knowledge = SingleFileKnowledge(config, rules_txt, logger=logger)
    knowledge = _add_indices_to_knowledge(knowledge, index_txt)
    joblib.dump(knowledge, config.get_value("index_filename"))
    return knowledge


def add_to_index(path):
    config = Configuration.load_local_config()
    index_filename = config.get_value("index")
    with open(index_filename) as file:
        indices = yaml.safe_load(file.read())
        if path in indices["paths"]:
            return

        indices["paths"].append(path)

    with open(index_filename, "w") as file:
        yaml.dump(indices, file)