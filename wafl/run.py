import logging
from logging import getLogger
from wafl.config import Configuration
from wafl.exceptions import CloseConversation
from wafl.conversation.conversation import Conversation
from wafl.interface.command_line_interface import CommandLineInterface
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.testcases import ConversationTestCases

_logger = getLogger(__file__)


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
    if config.get_value("voice_hotwords"):
        interface.add_hotwords(config.get_value("voice_hotwords"))

    conversation = Conversation(
        knowledge, interface=interface, code_path="functions", config=config
    )
    conversation.output("Please say 'Computer' to activate me")

    activation_word = "computer"
    interface.add_hotwords(activation_word)
    max_misses = 3
    while True:
        try:
            result = conversation.input(activation_word=activation_word)
            num_misses = 0
            print("RESULT:", result)

            if result:
                interface.check_understanding(True)

            if (
                interface.check_understanding()
                and not result
                and not interface.bot_has_spoken()
            ):
                interface.play_deny_sound()
                print("NUM_MISSES:", num_misses)
                num_misses += 1
                if num_misses >= max_misses:
                    interface.check_understanding(False)

        except CloseConversation:
            print("Closing conversation")
            _logger.info("Closing conversation")
            activation_word = "computer"
            interface.check_understanding(False)
            continue

        except (KeyboardInterrupt, EOFError):
            break

    conversation.output("Good bye!")


def run_testcases():
    knowledge = Knowledge(open("rules.wafl").read())
    test_cases_text = open("testcases.txt").read()
    testcases = ConversationTestCases(test_cases_text, knowledge)
    testcases.run()
