import random

from wafl.config import Configuration
from wafl.exceptions import CloseConversation
from wafl.conversation.conversation import Conversation
from wafl.interface.command_line_interface import CommandLineInterface
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.testcases import ConversationTestCases
from wafl.variables import get_variables

_logger = LocalFileLogger()


def print_incipit():
    print()
    print(f"Running WAFL version {get_variables()['version']}.")
    print()


def run_from_command_line():
    print_incipit()
    interface = CommandLineInterface()
    conversation = Conversation(
        ProjectKnowledge("rules.wafl", logger=_logger),
        interface=interface,
        code_path="/",
        logger=_logger,
    )
    conversation.output("Hello. How may I help you?")

    while True:
        try:
            conversation.input()
        except (CloseConversation, KeyboardInterrupt, EOFError):
            break

    conversation.output("Goodbye!")


def run_from_audio():
    print_incipit()
    config = Configuration.load_local_config()
    knowledge = ProjectKnowledge("rules.wafl", logger=_logger)
    interface = VoiceInterface(config)
    interface.check_understanding(False)
    conversation = Conversation(
        knowledge,
        interface=interface,
        code_path=knowledge.get_dependencies_list(),
        config=config,
        logger=_logger,
    )

    activation_word = config.get_value("waking_up_word")
    conversation.output(f"Please say '{activation_word}' to activate me")
    interface.add_hotwords(activation_word)
    num_misses = 0
    max_misses = 3
    interactions = 0
    while True:
        if not interface.check_understanding():
            interactions = 0
            num_misses = 0

        try:
            result = conversation.input(activation_word=activation_word)
            _logger.write(f"Conversation Result {result}", log_level=_logger.level.INFO)
            interactions += 1
            if result:
                interface.check_understanding(True)

            if interface.bot_has_spoken() and interactions == 1:
                interface.check_understanding(False)
                num_misses = 0

            if (
                interface.check_understanding()
                and not result
                and not interface.bot_has_spoken()
            ):
                num_misses += 1
                if num_misses >= max_misses:
                    interface.check_understanding(False)

                if interactions <= 1:
                    interface.output(random.choice(["What can I do for you?"]))

                else:
                    interface.output(random.choice(["Sorry?", "Can you repeat?"]))

            else:
                num_misses = 0

        except CloseConversation:
            _logger.write(f"Closing the conversation", log_level=_logger.level.INFO)
            interface.check_understanding(False)
            continue

        except (KeyboardInterrupt, EOFError):
            break

    conversation.output("Good bye!")


def run_testcases():
    knowledge = ProjectKnowledge("rules.wafl")
    test_cases_text = open("testcases.txt").read()
    testcases = ConversationTestCases(test_cases_text, knowledge)
    testcases.run()
