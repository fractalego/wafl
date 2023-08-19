from wafl.answerer.arbiter_answerer import ArbiterAnswerer
from wafl.answerer.list_answerer import ListAnswerer


def create_answerer(knowledge, interface, code_path, connector, logger):
    return ListAnswerer(
        [
            ArbiterAnswerer.create_answerer(
                knowledge, interface, code_path, connector, logger
            ),
        ],
        interface,
        logger,
    )
