import logging
import re
import traceback

from wafl.conversation.utils import is_question
from wafl.parsing.preprocess import import_module, create_preprocessed
from wafl.qa.qa import QA, Answer, Query
from inspect import getmembers, isfunction

_logger = logging.getLogger(__name__)


class BackwardInference:
    def __init__(
        self,
        knowledge: "Knowledge",
        interface: "Interface",
        module_name=None,
        max_depth: int = 4,
    ):
        self._max_depth = max_depth
        self._knowledge = knowledge
        self._interface = interface
        self._qa = QA()
        if module_name:
            create_preprocessed(module_name)
            self._module = import_module(module_name)
            self._functions = [item[0] for item in getmembers(self._module, isfunction)]

    def get_inference_answer(self, text):
        query = Query(text=text, is_question=is_question(text))
        answer = self._compute_recursively(query, already_matched={}, depth=1)

        if answer.text == "True":
            return True

        if answer.text == "False":
            return False

        return answer.text

    def compute(self, query):
        return self._compute_recursively(query, already_matched=set(), depth=0)

    def _compute_recursively(self, query: "Query", already_matched, depth):
        if depth > self._max_depth:
            return Answer(text="False")

        facts = self._knowledge.ask_for_facts(query)
        for fact in facts:
            answer = self._qa.ask(query, fact.text)
            if str(fact) in already_matched:
                continue

            return answer

        if depth > 0 and facts == [] and query.is_question:
            self._interface.output(query.text)
            user_input_text = self._interface.input()

            ### TODO: Make yes/no less naive (and add unknown as possible input from user)
            if user_input_text.lower() == "yes":
                user_answer = Answer(text="True")

            elif user_input_text.lower() == "no" or user_input_text.strip() == "":
                user_answer = Answer(text="False")

            else:
                user_answer = self._qa.ask(query, f"The user says: {user_input_text}")

            return user_answer

        rules = self._knowledge.ask_for_rule_backward(query)
        for rule in rules:
            index = 0
            substitutions = {}
            bot_has_spoken = False

            rule_effect_text = rule.effect.text

            if rule.effect.is_question:
                answer = self._qa.ask(rule.effect, query.text)

                if answer.text == "False":
                    continue

                if answer.variable:
                    substitutions[f"{{{answer.variable.strip()}}}"] = answer.text
                    substitutions[f"({answer.variable.strip()})"] = f'("{answer.text}")'
                    substitutions[f"({answer.variable.strip()},"] = f'("{answer.text}",'
                    substitutions[f",{answer.variable.strip()},"] = f',"{answer.text}",'
                    substitutions[f",{answer.variable.strip()})"] = f',"{answer.text}")'

            for cause in rule.causes:
                new_already_matched = already_matched.copy()

                cause_text = cause.text.strip()
                invert_results = False
                if cause_text[0] == "!":
                    invert_results = True
                    cause_text = cause_text[1:]

                for key, value in substitutions.items():
                    if "(" in cause_text:
                        cause_text = cause_text.replace(" ", "")

                    cause_text = cause_text.replace(key, str(value))

                if cause_text.lower().find("say") == 0:
                    utterance = cause_text[3:].strip().capitalize()
                    self._interface.output(utterance)
                    bot_has_spoken = True
                    answer = Answer(text="True")

                elif cause_text.lower().find("remember") == 0:
                    utterance = cause_text[8:].strip().capitalize()
                    self._knowledge.add(utterance)
                    answer = Answer(text="True")

                elif "(" in cause_text.lower():
                    if "=" in cause_text:
                        variable, to_execute = cause_text.split("=")
                        variable = variable.strip()
                        to_execute = to_execute.strip()

                    else:
                        to_execute = cause_text.strip()

                    try:
                        if any(item + "(" in to_execute for item in self._functions):
                            to_execute = add_self_to_function_arguments(to_execute)
                        result = eval(f"self._module.{to_execute}")

                    except Exception as e:
                        traceback.print_exc()
                        _logger.warning(str(e))
                        result = False

                    if "=" in cause_text:
                        substitutions.update({f"{{{variable}}}": result})
                        substitutions.update({f"({variable})": result})
                        substitutions.update({f"({variable},": result})
                        substitutions.update({f",{variable},": result})
                        substitutions.update({f",{variable})": result})

                    if result != False:
                        answer = Answer(text="True")

                    else:
                        answer = Answer(text="False")

                else:
                    if "=" in cause_text:
                        variable, text = cause_text.split("=")
                        variable = variable.strip()
                        text = text.strip()
                        new_query = Query(
                            text=text, is_question=True, variable=variable
                        )

                    elif cause.is_question:
                        new_query = Query(text=cause_text, is_question=True)

                    else:
                        new_query = Query(text=cause_text, is_question=False)

                    answer = self._compute_recursively(
                        new_query, new_already_matched, depth + 1
                    )

                if invert_results:
                    if answer.text == "False":
                        answer.text = "True"

                    if answer.text == "True":
                        answer.text = "False"

                if answer.text == "False":
                    break

                already_matched = new_already_matched
                if answer.variable:
                    substitutions[f"{{{answer.variable.strip()}}}"] = answer.text
                    substitutions[f"({answer.variable.strip()})"] = f'("{answer.text}")'
                    substitutions[f"({answer.variable.strip()},"] = f'("{answer.text}")'
                    substitutions[f",{answer.variable.strip()},"] = f'("{answer.text}")'
                    substitutions[f",{answer.variable.strip()})"] = f'("{answer.text}")'

                index += 1

            if index == len(rule.causes):
                for key, value in substitutions.items():
                    rule_effect_text = rule_effect_text.replace(key, value)

                answer = self._qa.ask(query, rule_effect_text)

                if answer.text == "False":
                    continue

                if answer.text.lower() == "yes" or bot_has_spoken:
                    answer.text = "True"

                return answer

        return Answer(text="False")


def add_self_to_function_arguments(text: str) -> str:
    text = re.sub("(.*\([\"'0-9a-zA-Z@\-\.,\s]+)\)$", "\\1, self)", text)
    text = re.sub("(.*)\(\)$", "\\1(self)", text)
    return text
