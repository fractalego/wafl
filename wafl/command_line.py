import os
import sys

from wafl.config import create_initial_files
from wafl.parsing.preprocess import remove_preprocessed
from wafl.run import (
    run_from_command_line,
    run_from_audio,
    run_testcases,
    print_incipit,
    download_models,
)
from wafl.runners.run_web_interface import run_server


def print_help():
    print("\n")
    print("These are the available commands:")
    print("> wafl init: Initialize the current folder")
    print("> wafl run-cli: Run a cli version of the chatbot")
    print("> wafl run-audio: Run a voice-powered version of the chatbot")
    print("> wafl run-tests: Run the tests in testcases.txt")
    print()


def add_cwd_to_syspath():
    sys.path.append(os.getcwd())


def process_cli():
    add_cwd_to_syspath()
    print_incipit()

    arguments = sys.argv
    if len(arguments) > 1:
        command = arguments[1]

        if command == "init":
            create_initial_files()
            download_models()

        elif command == "run-cli":
            run_from_command_line()
            remove_preprocessed("/")

        elif command == "run-audio":
            run_from_audio()
            remove_preprocessed("/")

        elif command == "run-server":
            run_server()
            remove_preprocessed("/")

        elif command == "run-tests":
            run_testcases()
            remove_preprocessed("/")

        elif command == "help":
            print_help()

        else:
            print("Unknown argument.\n")
            print_help()


def main():
    try:
        process_cli()

    except RuntimeError as e:
        print(e)
        print("WAFL ended due to the exception above.")
