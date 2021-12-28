from wafl.conversation.conversation import Conversation
from wafl.interface.command_line_interface import CommandLineInterface
from wafl.interface.voice_interface import VoiceInterface
from wafl.knowledge.knowledge import Knowledge


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
        except (KeyError, EOFError):
            break

    conversation.output("Goodbye!")


def run_from_audio():
    wafl_rules = open("rules.wafl").read()
    interface = VoiceInterface()
    conversation = Conversation(
        Knowledge(wafl_rules), interface=interface, code_path="functions"
    )
    conversation.output("Hello. Please say 'Computer' to activate me")

    activation_word = "computer"
    while True:
        try:
            if conversation.input(activation_word=activation_word):
                activation_word = ""

        except KeyboardInterrupt:
            activation_word = "computer"
            continue

        except (KeyError, EOFError):
            break

    conversation.output("Goodbye!")
