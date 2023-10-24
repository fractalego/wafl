from wafl.answerer.dialogue_answerer import DialogueAnswerer


def create_answerer(config, knowledge, interface, code_path, logger):
    return DialogueAnswerer(
        config, knowledge, interface, logger
    )
