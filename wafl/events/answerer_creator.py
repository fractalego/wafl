from wafl.answerer.arbiter_answerer import ArbiterAnswerer
from wafl.answerer.list_answerer import ListAnswerer


def create_answerer(config, knowledge, interface, code_path, logger):
    return ListAnswerer(
        [
            ArbiterAnswerer.create_answerer(
                config, knowledge, interface, code_path, logger
            ),
        ],
        interface,
        logger,
    )
