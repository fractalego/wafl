from wafl.config import Configuration
from wafl.parsing.preprocess import create_preprocessed

from wafl.exceptions import CloseConversation

from wafl.conversation.conversation import Conversation
from wafl.interface.command_line_interface import CommandLineInterface
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.testcases import ConversationTestCases


def run_from_command_line():
    wafl_rules = open("rules.wafl").read()
    interface = CommandLineInterface()
    conversation = Conversation(
        Knowledge(wafl_rules), interface=interface, code_path="functions"
    )
    conversation.output("Hello. How may I help you?")

    while True:
        try:
            conversation.input()
        except (CloseConversation, KeyboardInterrupt, EOFError):
            break

    conversation.output("Goodbye!")


def run_from_audio():
    config = Configuration.load_local_config()
    knowledge = Knowledge(open("rules.wafl").read())
    interface = VoiceInterface(config)
    interface.check_understanding(False)
    conversation = Conversation(
        knowledge, interface=interface, code_path="functions", config=config
    )
    conversation.output("Hello. Please say 'Computer' to activate me")

    activation_word = "computer"
    while True:
        try:
            if conversation.input(activation_word=activation_word):
                activation_word = ""

        except CloseConversation:
            activation_word = "computer"
            interface.check_understanding(False)
            continue

        except (KeyboardInterrupt, EOFError):
            break

    conversation.output("Goodbye!")


def run_testcases():
    knowledge = Knowledge(open("rules.wafl").read())
    test_cases_text = open("testcases.txt").read()
    testcases = ConversationTestCases(test_cases_text, knowledge)
    testcases.run()
