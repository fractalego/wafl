import sys

from wafl.config import create_initial_files
from wafl.parsing.preprocess import remove_preprocessed
from wafl.run import run_from_command_line, run_from_audio, run_testcases


def download_models():
    import nltk

    nltk.download("averaged_perceptron_tagger")


if __name__ == "__main__":
    print("WAFL v0\n")

    arguments = sys.argv
    if len(arguments) > 1:
        command = arguments[1]

        if command == "init":
            create_initial_files()
            download_models()

        if command == "run":
            run_from_command_line()
            remove_preprocessed("functions")

        if command == "run-audio":
            run_from_audio()
            remove_preprocessed("functions")

        if command == "test":
            run_testcases()
            remove_preprocessed("functions")
