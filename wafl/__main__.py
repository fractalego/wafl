import sys

from wafl.config import create_initial_files


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
