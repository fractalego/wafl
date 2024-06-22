import joblib
import os
import re
import yaml

from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.readers.reader_factory import ReaderFactory
from wafl.simple_text_processing.normalize import normalized


def input_is_valid(text):
    if not text.strip():
        return False

    if normalized(text) != "no" and len(text) <= 2:
        return False

    return True


def remove_text_between_brackets(text: str) -> str:
    return re.sub(r"(\[.*?\])", "", text)



def _add_indices_to_knowledge(knowledge, config, logger):
    filename = config.get_value("index")
    indices = yaml.safe_load(filename)
    for path in indices["paths"]:
        for root, _, files in os.walk(path):
            for file in files:
                with open(os.path.join(root, file)) as f:
                    reader = ReaderFactory.get_reader(file)
                    for chunk in reader.get_chunks(f.read()):
                        knowledge.add(chunk)


def load_knowledge(config, logger):
    if ".yaml" in config.get_value("rules") and not any(
        item in config.get_value("rules") for item in [" ", "\n"]   #### ALLOW INDEXING FROM rules.yaml
    ):
        with open(config.get_value("rules")) as file:
            rules_txt = file.read()

    else:
        rules_txt = config.get_value("rules")

    if os.path.exists(config.get_value("index_filename")):
        knowledge = joblib.load(config.get_value("index_filename"))
        if knowledge.hash == hash(rules_txt):
            return knowledge

    knowledge = SingleFileKnowledge(config, rules_txt, logger=logger)
    knowledge = _add_indices_to_knowledge(knowledge, config, logger)
    joblib.dump(knowledge, config.get_value("index_filename"))
    return knowledge
