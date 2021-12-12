import sys

from wafl.config import create_initial_files


if __name__ == "__main__":
    print('WAFL v0\n')

    arguments = sys.argv
    if len(arguments) > 1:
        command = arguments[1]

        if command == 'init':
            create_initial_files()
