import importlib
import os
import re
from inspect import getmembers, isfunction

_preprocessed_prefix = "__wafl_"
_functions_standard_name = "functions"
_python_functions_standard_name = _functions_standard_name + ".py"


def get_all_functions_names(module_name):
    module = importlib.import_module(module_name)
    functions = [item[0] for item in getmembers(module, isfunction)]
    return functions


def clean_module_name(name):
    if not name:
        raise RuntimeError(
            f"The name {name} is empty and cannot be used as a python module"
        )

    if name[0] == "/":
        name = name[1:]

    if name and name[-1] == "/":
        name = name[:-1]

    name = name.replace("/", ".")
    if name:
        name += "."

    return name


def create_preprocessed(module: str):
    function_names = get_all_functions_names(
        clean_module_name(module) + _functions_standard_name
    )
    filename = "." + module + "/" + _python_functions_standard_name
    with open(filename) as file:
        print(f"Preprocessing {filename}.")
        text = file.read()
        text = text.replace('{f"%', 'inference.get_inference_answer(f"')
        text = text.replace('{"%', 'inference.get_inference_answer(f"')
        text = text.replace('%"}', '", task_memory)')

        for name in function_names:
            text = re.sub(
                f"({name}\([0-9a-zA-Z,\s:]+)\)",
                "\\1, inference, task_memory)",
                text,
            )
            text = re.sub(f"({name})\(\)", "\\1(inference, task_memory)", text)

    preprocessed_filename = filename.replace(
        _python_functions_standard_name,
        _preprocessed_prefix + _python_functions_standard_name,
    )
    with open(preprocessed_filename, "w") as file:
        file.write(text)


def import_module(module_name):
    module_name = (
        clean_module_name(module_name) + _preprocessed_prefix + _functions_standard_name
    )
    return importlib.import_module(module_name)


def remove_preprocessed(module):
    print("Removing preprocessed files")
    filename = module + ".py"
    if os.path.isfile(filename):
        os.remove(_preprocessed_prefix + filename)
