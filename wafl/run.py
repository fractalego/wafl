from wafl.conversation.conversation import Conversation
from wafl.interface import CommandLineInterface
from wafl.knowledge.knowledge import Knowledge


def run_from_command_line():
    wafl_rules = open("rules.wafl").read()
    interface = CommandLineInterface()
    conversation = Conversation(Knowledge(wafl_rules), interface=interface)
    conversation.output("Welcome to the website. How may I help you?")

    while True:
        try:
            input_from_user = input("user> ")
        except (KeyError, EOFError):
            break
        conversation.input(input_from_user)

    conversation.output("Goodbye!")
