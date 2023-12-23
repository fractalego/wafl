import asyncio

from wafl.config import Configuration
from wafl.exceptions import CloseConversation
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.command_line_interface import CommandLineInterface
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.testcases import ConversationTestCases
from wafl.variables import get_variables

_logger = LocalFileLogger()


def print_incipit():
    print()
    print(f"Running WAFL version {get_variables()['version']}.")
    print()


def run_from_command_line():
    interface = CommandLineInterface()
    config = Configuration.load_local_config()
    conversation_events = ConversationEvents(
        config=config,
        interface=interface,
        logger=_logger,
    )
    asyncio.run(interface.output("Hello. How may I help you?"))

    while True:
        try:
            asyncio.run(conversation_events.process_next())
        except (CloseConversation, KeyboardInterrupt, EOFError):
            break

    asyncio.run(interface.output("Goodbye!"))


def run_testcases():
    print("Running the testcases in testcases.txt\n")
    config = Configuration.load_local_config()
    test_cases_text = open("testcases.txt").read()
    testcases = ConversationTestCases(
        config,
        test_cases_text,
        logger=_logger,
    )
    asyncio.run(testcases.run())


def download_models():
    import nltk

    nltk.download("averaged_perceptron_tagger")
