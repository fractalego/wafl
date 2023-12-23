from wafl.answerer.dialogue_answerer import DialogueAnswerer


def create_answerer(config, knowledge, interface, logger):
    return DialogueAnswerer(
        config, knowledge, interface, config.get_value("functions"), logger
    )
