import json
import os
import shutil

_path = os.path.dirname(__file__)


def create_initial_files():
    _sample_project_dir = os.path.join(_path, "templates/")
    print("+ Initializing ... ", end="")
    shutil.copytree(_sample_project_dir, "./", dirs_exist_ok=True)

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
