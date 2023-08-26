import re

from typing import List, Dict, Tuple, Any
from fuzzywuzzy import process
from wafl.extractors.dataclasses import Answer
from wafl.simple_text_processing.normalize import normalized
from wafl.simple_text_processing.questions import is_question


def cause_is_negated(cause_text: str) -> bool:
    return cause_text.find("!") == 0


def check_negation(cause_text: str) -> Tuple[str, bool]:
    invert_results = False
    if cause_is_negated(cause_text):
        if cause_text[0] == "!":
            invert_results = True
            cause_text = cause_text[1:]

    return cause_text, invert_results


def text_is_code(text: str) -> bool:
    if "(" in text:
        return True

    return False


def _make_safe(text: str) -> str:
    text = str(text)
    text = text.replace('"', "'")
    text = text.replace("''", "'")
    text = text.replace('""', '"')
    text = text.replace(r"\"", '\\"')
    text = text.replace(r"\'", "\\'")
    return text


def apply_substitutions(cause_text: str, substitutions: Dict[str, str]) -> str:
    if text_is_code(cause_text):
        cause_text = cause_text.replace(" ", "")

    for key, value in substitutions.items():
        safe_value = _make_safe(str(value))
        cause_text = cause_text.replace(key, safe_value)

    return cause_text


def text_has_say_command(text: str) -> bool:
    words = text.strip().split()
    if words:
        return words[0].lower() == "say"

    return False


def text_has_retrieve_command(text: str) -> bool:
    words = text.split("=")[-1].strip().split()
    if words:
        return words[0].lower() == "retrieve"

    return False


def text_has_remember_command(text: str) -> bool:
    return normalized(text).find("remember") == 0


def text_has_new_task_memory_command(text: str) -> bool:
    return normalized(text).find("erase memory") == 0


def update_substitutions_from_answer(answer: "Answer", substitutions: Dict[str, str]):
    safe_value = _make_safe(answer.text)
    substitutions[f"({{{answer.variable.strip()}}})"] = f'("{safe_value}")'
    substitutions[f"({{{answer.variable.strip()}}},"] = f'("{safe_value}",'
    substitutions[f",{{{answer.variable.strip()}}},"] = f',"{safe_value}",'
    substitutions[f",{{{answer.variable.strip()}}})"] = f',"{safe_value}")'
    substitutions[f"{{{answer.variable.strip()}}}"] = safe_value
    substitutions[f"({answer.variable.strip()})"] = f'("{safe_value}")'
    substitutions[f"({answer.variable.strip()},"] = f'("{safe_value}",'
    substitutions[f",{answer.variable.strip()},"] = f',"{safe_value}",'
    substitutions[f",{answer.variable.strip()})"] = f',"{safe_value}")'


def add_function_arguments(text: str) -> str:
    text = re.sub(
        "(.*\([\"'0-9a-zA-Z@?':\-_\.,\s]+)\)$", "\\1, self, policy, task_memory)", text
    )
    text = re.sub("(.*)\(\)$", "\\1(self, policy, task_memory)", text)
    return text


def update_substitutions_from_results(
    result: str, variable: str, substitutions: Dict[str, str]
):
    safe_value = _make_safe(result)
    substitutions.update({f"({{{variable}}})": f'("{safe_value}")'})
    substitutions.update({f"({{{variable}}},": f'("{safe_value}",'})
    substitutions.update({f",{{{variable}}},": f',"{safe_value}",'})
    substitutions.update({f",{{{variable}}})": f',"{safe_value}")'})
    substitutions.update({f"{{{variable}}}": safe_value})
    substitutions.update({f"({variable})": f'("{safe_value}")'})
    substitutions.update({f"({variable},": f'("{safe_value}",'})
    substitutions.update({f",{variable},": f',"{safe_value}",'})
    substitutions.update({f",{variable})": f',"{safe_value}")'})


def invert_answer(answer: "Answer") -> "Answer":
    if answer.text == "False":
        return Answer(text="True")

    if answer.text == "True":
        return Answer(text="False")

    if answer.text == "No":
        return Answer(text="Yes")

    if answer.text == "Yes":
        return Answer(text="No")

    return answer


def text_has_assigmnent(cause_text: str) -> bool:
    return "=" in cause_text


def process_unknown_answer(answer: "Answer") -> bool:
    if normalized(answer.text) == "unknown":
        answer = None

    return answer


def cluster_facts(facts_and_threshold: List[Tuple["Fact", float]]) -> List[str]:
    if not facts_and_threshold:
        return []

    _cluster_margin = 0.1

    texts = []
    last_threshold = facts_and_threshold[0][1]
    text = ""
    prior_facts = set()
    for fact, threshold in facts_and_threshold:
        if not fact.text:
            continue

        if fact.text in prior_facts:
            continue

        prior_facts.add(fact.text)

        if abs(threshold - last_threshold) < _cluster_margin:
            text += normalized(fact.text, lower_case=False).capitalize() + ". "

        else:
            texts.append(text.strip())
            text = ""
            last_threshold = threshold

    if text:
        texts.append(text.strip())

    return texts


def selected_answer(candidate_answers: List["Answer"], variable_name: str) -> bool:
    for answer in candidate_answers:
        if answer and normalized(answer.text) != "unknown":
            return answer

    for answer in candidate_answers:
        if answer:
            return answer

    return_answer = Answer.create_neutral()
    return_answer.variable = variable_name
    return return_answer


def fact_relates_to_user(text: str) -> bool:
    if "the user" in normalized(text):
        return True

    return False


def project_answer(answer: "Answer", candidates: List[str]) -> "Answer":
    if not candidates or not answer_is_informative(answer):
        return Answer(text="unknown")

    extracted, score = process.extract(answer.text, candidates, limit=1)[0]
    if score < 60:
        return Answer(text="unknown")

    return Answer(text=extracted)


def answer_is_informative(answer: "Answer") -> bool:
    return not any(item == normalized(answer.text) for item in ["unknown"])


def is_inference_task(text):
    text = text.split("=")[-1]
    prompt = "the user"
    if text.strip().lower().find(prompt) == 0:
        return True

    return False


async def text_is_text_generation_task(
    text: str,
    entailer: "Entailer",
) -> bool:
    if not "=" in text:
        return False

    if text_is_code(text):
        return False

    if is_inference_task(text):
        return False

    if is_question(text.split("=")[1]):
        return False

    if await entailer.entails(
        text,
        f"An instruction or request of some kind",
        return_threshold=True,
        threshold=0.5,
    ):
        return True

    return False


def escape_characters(text: str) -> str:
    text = text.replace("\n", "\\n")
    return text


def string_is_python_list(text: str) -> bool:
    try:
        result = eval(text)
        if type(result) == list:
            return True

    except (SyntaxError, NameError):
        try:
            text = text.replace("'s", "\\'s")
            result = eval(text)
            if type(result) == list:
                return True

        except (SyntaxError, NameError):
            pass

        pass

    return False


def get_list_from_string(text: str) -> List[Any]:
    try:
        result = eval(text)
        if type(result) == list:
            return result

    except (SyntaxError, NameError):
        text = text.replace("'s", "\\'s")
        result = eval(text)
        if type(result) == list:
            return result

        pass

    return []


def get_list_like_element(text: str) -> str:
    start_pos = text.find("[")
    if start_pos == -1:
        return ""

    end_pos = text.find("]", start_pos)
    if end_pos == -1:
        return ""

    return text[start_pos : end_pos + 1]


def create_python_list_from_bullet_list(text: str) -> List[str]:
    new_list = text.split("\n")
    if len(new_list) != 1:
        return new_list

    new_list = text.split("', '")
    if len(new_list) != 1:
        return new_list

    new_list = text.split(",")
    if len(new_list) != 1:
        return new_list

    return [text]


def get_causes_list(text: str) -> List[str]:
    """
    If the text contains a Python list (e.g. generate a chapter with the theme ["space", "romance"] )
    then the output becomes a list of texts where each item appears separaterly
    (e.g. ["generate a chapter with the theme space", generate a chapter with the theme romance"]

    :param text:
    :return: a list of causes,
    """
    if text_is_code(text):
        return [text]

    list_like_element = get_list_like_element(text)
    if not list_like_element:
        return [text]

    if not string_is_python_list(list_like_element):
        items = create_python_list_from_bullet_list(list_like_element[1:-1])

    else:
        items = get_list_from_string(list_like_element)

    causes_list = []
    for item in items:
        causes_list.append(text.replace(list_like_element, item))

    return causes_list


def create_default_substitutions(interface: "BaseInterface") -> Dict[str, str]:
    substitutions = {}
    dialogue = " ".join(interface.get_utterances_list())
    update_substitutions_from_results(dialogue, "_dialogue", substitutions)
    return substitutions
