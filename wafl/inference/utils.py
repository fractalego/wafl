import re

from typing import List
from fuzzywuzzy import process
from wafl.qa.dataclasses import Answer


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


def _make_safe(text):
    text = str(text)
    text = text.replace('"', "'")
    text = text.replace("''", "'")
    text = text.replace('""', '"')
    return text


def apply_substitutions(cause_text, substitutions):
    if text_is_code(cause_text):
        cause_text = cause_text.replace(" ", "")

    for key, value in substitutions.items():
        safe_value = _make_safe(str(value))
        cause_text = cause_text.replace(key, safe_value)

    return cause_text


def text_has_say_command(text):
    words = text.strip().split()
    if words:
        return words[0].lower() == "say"

    return False


def text_has_remember_command(text):
    return normalized(text).find("remember") == 0


def text_has_new_task_memory_command(text):
    return normalized(text).find("erase memory") == 0


def update_substitutions_from_answer(answer, substitutions):
    safe_value = _make_safe(answer.text)
    substitutions[f"{{{answer.variable.strip()}}}"] = safe_value
    substitutions[f"({answer.variable.strip()})"] = f'("{safe_value}")'
    substitutions[f"({answer.variable.strip()},"] = f'("{safe_value}",'
    substitutions[f",{answer.variable.strip()},"] = f',"{safe_value}",'
    substitutions[f",{answer.variable.strip()})"] = f',"{safe_value}")'


def add_function_arguments(text: str) -> str:
    text = re.sub(
        "(.*\([\"'0-9a-zA-Z@?':\-\.,\s]+)\)$", "\\1, self, task_memory)", text
    )
    text = re.sub("(.*)\(\)$", "\\1(self, task_memory)", text)
    return text


def update_substitutions_from_results(result, variable, substitutions):
    safe_value = _make_safe(result)
    substitutions.update({f"{{{variable}}}": safe_value})
    substitutions.update({f"({variable})": f'("{safe_value}")'})
    substitutions.update({f"({variable},": f'("{safe_value}",'})
    substitutions.update({f",{variable},": f',"{safe_value}",'})
    substitutions.update({f",{variable})": f',"{safe_value}")'})


def invert_answer(answer):
    if answer.text == "False":
        return Answer(text="True")

    if answer.text == "True":
        return Answer(text="False")

    if answer.text == "No":
        return Answer(text="Yes")

    if answer.text == "Yes":
        return Answer(text="No")

    return answer


def text_has_assigmnent(cause_text):
    return "=" in cause_text


def process_unknown_answer(answer):
    if normalized(answer.text) == "unknown":
        answer = None

    return answer


def normalized(text, lower_case=True):
    text = text.strip()
    if not text:
        return ""

    if text[-1] == ".":
        text = text[:-1]

    if lower_case:
        text = text.lower()

    return text.strip()


def cluster_facts(facts_and_threshold):
    if not facts_and_threshold:
        return []

    _cluster_margin = 0.1

    texts = []
    last_threshold = facts_and_threshold[0][1]
    text = ""
    for fact, threshold in facts_and_threshold:
        if not fact.text:
            continue

        if abs(threshold - last_threshold) < _cluster_margin:
            text += normalized(fact.text, lower_case=False) + ". "

        else:
            texts.append(text.strip())
            text = ""
            last_threshold = threshold

    if text:
        texts.append(text.strip())

    return texts


def selected_answer(candidate_answers):
    for answer in candidate_answers:
        if answer and normalized(answer.text) != "unknown":
            return answer

    for answer in candidate_answers:
        if answer:
            return answer

    return Answer(text="False")


def fact_relates_to_user(text):
    if "the user" in normalized(text):
        return True

    return False


def project_answer(answer: "Answer", candidates: List) -> "Answer":
    if not candidates:
        return Answer(text="unknown")

    extracted, score = process.extract(answer.text, candidates, limit=1)[0]
    if score < 60:
        return Answer(text="unknown")

    return Answer(text=extracted)
