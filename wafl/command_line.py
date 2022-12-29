import sys

from wafl.config import create_initial_files
from wafl.parsing.preprocess import remove_preprocessed
from wafl.run import run_from_command_line, run_from_audio, run_testcases, print_incipit


def download_models():
    import nltk

    nltk.download("averaged_perceptron_tagger")


def print_help():
    print("\n")
    print("> wafl init: Initialize the current folder")
    print("> wafl run-cli: Run a cli version of the chatbot")
    print("> wafl run-audio: Run a voice-powered version of the chatbot")
    print("> wafl run-tests: Run the tests in testcases.txt")
    print()


def main():
    print_incipit()

    arguments = sys.argv
    if len(arguments) > 1:
        command = arguments[1]

        if command == "init":
            create_initial_files()
            download_models()

        if command == "run-cli":
            run_from_command_line()
            remove_preprocessed("/")

        if command == "run-audio":
            run_from_audio()
            remove_preprocessed("/")

        if command == "run-tests":
            run_testcases()
            remove_preprocessed("/")

        if command == "help":
            print_help()

        else:
            print("Unknown argument.\n")
            print_help()


if __name__ == "__main__":
    main()
