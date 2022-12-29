import random

from wafl.config import Configuration
from wafl.exceptions import CloseConversation
from wafl.conversation.conversation import Conversation
from wafl.interface.command_line_interface import CommandLineInterface
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.scheduler.scheduler import Scheduler
from wafl.testcases import ConversationTestCases
from wafl.variables import get_variables

_logger = LocalFileLogger()


def print_incipit():
    print()
    print(f"Running WAFL version {get_variables()['version']}.")
    print()


def run_from_command_line():
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
            conversation.next()
        except (CloseConversation, KeyboardInterrupt, EOFError):
            break

    conversation.output("Goodbye!")


def run_from_audio():
    config = Configuration.load_local_config()
    knowledge = ProjectKnowledge("rules.wafl", logger=_logger)
    interface = VoiceInterface(config)
    conversation = Conversation(
        knowledge,
        interface=interface,
        code_path=knowledge.get_dependencies_list(),
        config=config,
        logger=_logger,
    )
    scheduler = Scheduler(
        interface,
        conversation,
        _logger,
        activation_word=config.get_value("waking_up_word"),
    )
    scheduler.run(max_misses=3)


def run_testcases():
    print("Running the testcases in testcases.txt\n")
    knowledge = ProjectKnowledge("rules.wafl")
    test_cases_text = open("testcases.txt").read()
    testcases = ConversationTestCases(
        test_cases_text,
        knowledge,
        code_path=knowledge.get_dependencies_list(),
        logger=_logger,
    )
    testcases.run()
