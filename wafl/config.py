import json
import os

_path = os.path.dirname(__file__)


def create_initial_files():
    _rules_template = open(os.path.join(_path, "templates/rules.wafl"))
    _functions_template = open(os.path.join(_path, "templates/functions.py"))
    _events_template = open(os.path.join(_path, "templates/events.py"))
    _config_template = open(os.path.join(_path, "templates/config.json"))
    _testcases_template = open(os.path.join(_path, "templates/testcases.txt"))
    _docker_start = open(os.path.join(_path, "templates/start_llm.sh"))

    print("+ Initializing ... ", end="")

    with open("rules.wafl", "w") as file:
        file.write(_rules_template.read())

    with open("functions.py", "w") as file:
        file.write(_functions_template.read())

    with open("config.json", "w") as file:
        file.write(_config_template.read())

    with open("testcases.txt", "w") as file:
        file.write(_testcases_template.read())

    with open("events.py", "w") as file:
        file.write(_testcases_template.read())

    with open("start_llm.sh", "w") as file:
        file.write(_docker_start.read())

    os.mkdir("logs/")

    print("Done.")


class Configuration:
    def __init__(self, filename):
        with open(filename) as file:
            self._data = json.load(file)

    def get_value(self, key):
        if key in self._data:
            return self._data[key]

        print(
            f"The value '{key}' does not appear in the configuration. Should you add it?"
        )

    def set_value(self, key, value):
        if key not in self._data:
            raise ValueError(f"Key '{key}' does not exist in the config file")

        self._data[key] = value

    @classmethod
    def load_local_config(cls):
        try:
            return cls("config.json")

        except FileNotFoundError:
            print(
                "Cannot load 'config.json'. Does the file exist in the execution path?"
            )
            exit(0)
