import importlib
import os
import re
from inspect import getmembers, isfunction

preprocessed_prefix = "__wafl_"


def get_all_functions_names(module_name):
    module = importlib.import_module(module_name)
    functions = [item[0] for item in getmembers(module, isfunction)]
    return functions


def create_preprocessed(module: str):
    function_names = get_all_functions_names(module)
    filename = module + ".py"  ### TODO: This is not enough in general
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

    with open(preprocessed_prefix + filename, "w") as file:
        file.write(text)


def import_module(module_name):
    return importlib.import_module(f"{preprocessed_prefix + module_name}")


def remove_preprocessed(module):
    print("Removing preprocessed files")
    filename = module + ".py"
    if os.path.isfile(filename):
        os.remove(preprocessed_prefix + filename)
