import re

from wafl.qa.qa import Answer


def cause_is_negated(cause_text):
    return cause_text.find("!") == 0


def check_negation(cause_text):
    invert_results = False
    if cause_is_negated(cause_text):
        if cause_text[0] == "!":
            invert_results = True
            cause_text = cause_text[1:]

    return cause_text, invert_results


def text_is_code(text):
    if "(" in text:
        return True

    return False


def apply_substitutions(cause_text, substitutions):
    if text_is_code(cause_text):
        cause_text = cause_text.replace(" ", "")

    for key, value in substitutions.items():
        cause_text = cause_text.replace(key, str(value))

    return cause_text


def text_has_say_command(text):
    words = text.strip().split()
    if words:
        return words[0].lower() == "say"

    return False


def text_has_remember_command(text):
    return text.lower().find("remember") == 0


def update_substitutions_from_answer(answer, substitutions):
    substitutions[f"{{{answer.variable.strip()}}}"] = answer.text
    substitutions[f"({answer.variable.strip()})"] = f'("{answer.text}")'
    substitutions[f"({answer.variable.strip()},"] = f'("{answer.text}",'
    substitutions[f",{answer.variable.strip()},"] = f',"{answer.text}",'
    substitutions[f",{answer.variable.strip()})"] = f',"{answer.text}")'


def add_function_arguments(text: str) -> str:
    text = re.sub("(.*\([\"'0-9a-zA-Z@\-\.,\s]+)\)$", "\\1, self)", text)
    text = re.sub("(.*)\(\)$", "\\1(self)", text)
    return text


def update_substitutions_from_results(result, variable, substitutions):
    substitutions.update({f"{{{variable}}}": result})
    substitutions.update({f"({variable})": result})
    substitutions.update({f"({variable},": result})
    substitutions.update({f",{variable},": result})
    substitutions.update({f",{variable})": result})


def invert_answer(answer):
    if answer.text == "False":
        return Answer(text="True")

    if answer.text == "True":
        return Answer(text="False")

    return answer


def text_has_assigmnent(cause_text):
    return "=" in cause_text
