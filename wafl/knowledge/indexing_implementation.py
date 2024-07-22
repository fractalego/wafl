import os

import joblib
import yaml

from wafl.config import Configuration
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.readers.reader_factory import ReaderFactory


async def _add_indices_to_knowledge(knowledge, text):
    indices = yaml.safe_load(text)
    if "paths" not in indices or not indices["paths"]:
        return knowledge

    for path in indices["paths"]:
        for root, _, files in os.walk(path):
            for file in files:
                reader = ReaderFactory.get_reader(file)
                for chunk in reader.get_chunks(os.path.join(root, file)):
                    await knowledge.add_fact(chunk)

    return knowledge


async def load_knowledge(config, logger=None):
    if ".yaml" in config.get_value("rules") and not any(
        item in config.get_value("rules") for item in [" ", "\n"]
    ):
        with open(config.get_value("rules")) as file:
            rules_txt = file.read()

    else:
        rules_txt = config.get_value("rules")

    index_filename = config.get_value("index")
    if not os.path.exists(index_filename):
        raise RuntimeError(f"Index file {index_filename} does not exist.")
    with open(index_filename) as file:
        index_txt = file.read()

    cache_filename = config.get_value("cache_filename")
    if os.path.exists(cache_filename):
        knowledge = joblib.load(cache_filename)
        if knowledge.hash == hash(rules_txt) and os.path.getmtime(
            cache_filename
        ) > os.path.getmtime(index_filename):
            await knowledge.initialize_retrievers()
            return knowledge

    knowledge = SingleFileKnowledge(config, rules_txt, logger=logger)
    knowledge = await _add_indices_to_knowledge(knowledge, index_txt)
    joblib.dump(knowledge, config.get_value("cache_filename"))
    await knowledge.initialize_retrievers()
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
