import importlib
import os
import re

preprocessed_prefix = "__wafl_"


def create_preprocessed(module: str):
    filename = module + ".py"  ### TODO: This is not enough in general
    with open(filename) as file:
        text = file.read()
        text = text.replace('{"%', 'inference.get_inference_answer(f"')
        text = text.replace('%"}', '")')
        text = re.sub("(def .*\([0-9a-zA-Z,\s:]+)\):", "\\1, inference):", text)
        text = re.sub("(def .*)\(\):", "\\1(inference):", text)

    with open(preprocessed_prefix + filename, "w") as file:
        file.write(text)


def import_module(module_name):
    return importlib.import_module(f"{preprocessed_prefix + module_name}")


def remove_preprocessed(module):
    filename = module + ".py"
    os.remove(preprocessed_prefix + filename)
