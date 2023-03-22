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


def create_preprocessed(
    module: str,
    functions_standard_name=_functions_standard_name,
    python_functions_standard_name=_python_functions_standard_name,
):
    function_names = get_all_functions_names(
        clean_module_name(module) + functions_standard_name
    )
    filename = "." + module + "/" + python_functions_standard_name
    with open(filename) as file:
        print(f"Preprocessing {filename}.")
        text = file.read()
        text = re.sub(
            r'f?"%(.*)%"',
            'await inference.get_inference_answer(f"\\1", policy, task_memory)',
            text,
        )
        for name in function_names:
            text = re.sub(
                f" ({name}\([0-9a-zA-Z,\s:_]+)\)",
                " \\1, inference, policy, task_memory)",
                text,
            )
            text = re.sub(
                f" ({name})\(\)", " \\1(inference, policy, task_memory)", text
            )
            text = re.sub(
                f"(def {name}\()",
                "async \\1",
                text,
            )
            text = re.sub(f" ({name})\(", " await \\1(", text)
            text = re.sub(f'"[\s]*await ({name})\(', '"\\1(', text)

        text = text.replace("def await", "def")

    preprocessed_filename = filename.replace(
        _python_functions_standard_name,
        _preprocessed_prefix + _python_functions_standard_name,
    )
    with open(preprocessed_filename, "w") as file:
        file.write(text)


def import_module(
    module_name,
    preprocessed_prefix=_preprocessed_prefix,
    functions_standard_name=_functions_standard_name,
):
    module_name = (
        clean_module_name(module_name) + preprocessed_prefix + functions_standard_name
    )
    return importlib.import_module(module_name)


def remove_preprocessed(
    module, python_functions_standard_name=_python_functions_standard_name
):
    print("Removing preprocessed files")
    filename = (
        "." + module + "/" + _preprocessed_prefix + python_functions_standard_name
    )
    if os.path.isfile(filename):
        os.remove(filename)
