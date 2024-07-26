import os
import sys

from wafl.config import create_initial_files
from wafl.knowledge.indexing_implementation import add_to_index
from wafl.parsing.preprocess import remove_preprocessed
from wafl.run import (
    run_from_command_line,
    run_testcases,
    print_incipit,
    download_models,
    load_indices,
)
from wafl.runners.run_from_actions import run_action


def print_help():
    print("\n")
    print("These are the available commands:")
    print("> wafl init: Initialize the current folder")
    print("> wafl add <PATH>: Add the file or folder at <PATH> to the index")
    print(
        "> wafl run: Starts the chatbot on the web interface and the audio interface."
    )
    print("> wafl run-cli: Run a cli version of the chatbot")
    print("> wafl run-audio: Run a voice-powered version of the chatbot")
    print("> wafl run-server: Run a webserver version of the chatbot")
    print("> wafl run-tests: Run the tests in testcases.txt")
    print("> wafl add <PATH>: Add the file or folder at <PATH> to the index")
    print(
        "> wafl run-action <ACTION_NAME>: Run the action <ACTION_NAME> from actions.yaml"
    )
    print("> wafl help: Show this help message")
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

        elif command == "run":
            from wafl.runners.run_web_and_audio_interface import run_app

            load_indices()
            run_app()
            remove_preprocessed("/")

        elif command == "run-cli":
            load_indices()
            run_from_command_line()
            remove_preprocessed("/")

        elif command == "run-audio":
            from wafl.runners.run_from_audio import run_from_audio

            load_indices()
            run_from_audio()
            remove_preprocessed("/")

        elif command == "run-server":
            from wafl.runners.run_web_interface import run_server_only_app

            load_indices()
            run_server_only_app()
            remove_preprocessed("/")

        elif command == "run-tests":
            load_indices()
            run_testcases()
            remove_preprocessed("/")

        elif command == "run-action":
            if len(arguments) > 2:
                action_name = arguments[2]
                run_action(action_name)

            else:
                print("Please provide the action name as the second argument.")

        elif command == "add":
            if len(arguments) > 2:
                path = arguments[2]
                add_to_index(path)

            else:
                print("Please provide the path as the second argument.")

        elif command == "help":
            print_help()

        else:
            print("Unknown argument.\n")
    else:
        print_help()


def main():
    try:
        process_cli()

    except RuntimeError as e:
        print(e)
        print("WAFL ended due to the exception above.")
