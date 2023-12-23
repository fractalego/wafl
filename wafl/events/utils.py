import re

from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.simple_text_processing.normalize import normalized


def input_is_valid(text):
    if not text.strip():
        return False

    if normalized(text) != "no" and len(text) <= 2:
        return False

    return True


def remove_text_between_brackets(text: str) -> str:
    return re.sub(r"(\[.*?\])", "", text)


def load_knowledge(config, logger):
    if ".yaml" in config.get_value("rules") and not any(
        item in config.get_value("rules") for item in [" ", "\n"]
    ):
        with open(config.get_value("rules")) as file:
            rules_txt = file.read()

    else:
        rules_txt = config.get_value("rules")

    return SingleFileKnowledge(config, rules_txt, logger=logger)
