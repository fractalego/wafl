import json
import os
import shutil

_path = os.path.dirname(__file__)


def create_initial_files():
    _events_template = open(os.path.join(_path, "templates/events.py"))
    _config_template = open(os.path.join(_path, "templates/config.json"))
    _testcases_template = open(os.path.join(_path, "templates/testcases.txt"))
    _docker_start = open(os.path.join(_path, "templates/start_llm.sh"))
    _sample_project_dir = os.path.join(_path, "templates/sample_project/")

    print("+ Initializing ... ", end="")

    shutil.copytree(_sample_project_dir, "./", dirs_exist_ok=True)

    with open("config.json", "w") as file:
        file.write(_config_template.read())

    with open("testcases.txt", "w") as file:
        file.write(_testcases_template.read())

    with open("events.py", "w") as file:
        file.write(_testcases_template.read())

    with open("start_llm.sh", "w") as file:
        file.write(_docker_start.read())

    if not os.path.exists("logs/"):
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

    @classmethod
    def load_from_filename(cls, filename):
        try:
            return cls(filename)

        except FileNotFoundError:
            print(
                f"Cannot load '{filename}'. Does the file exist in the execution path?"
            )
            exit(0)
