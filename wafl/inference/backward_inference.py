import logging
import re
import traceback

from wafl.conversation.utils import is_question
from wafl.conversation.working_memory import WorkingMemory
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
        answer = self._compute_recursively(query, WorkingMemory(), depth=1)

        if answer.text == "True":
            return True

        if answer.text == "False":
            return False

        return answer.text

    def compute(self, query, working_memory=None):
        if not working_memory:
            working_memory = WorkingMemory()

        return self._compute_recursively(query, working_memory, depth=0)

    def _look_for_answer_in_facts(self, query, working_memory):
        facts = self._knowledge.ask_for_facts(query)
        for fact in facts:
            answer = self._qa.ask(query, fact.text)

            working_memory.add_story(fact.text)
            return True, answer

        return False, None

    def _compute_recursively(self, query: "Query", working_memory, depth):
        if depth > self._max_depth:
            return Answer(text="False")

        answer_is_found, answer = self._look_for_answer_in_facts(query, working_memory)
        if answer_is_found:
            return answer

        if query.is_question and depth > 0 and working_memory.get_story():
            answer = self._qa.ask(query, working_memory.get_story())
            if answer.text.lower().replace('.', '') not in ['unknown', 'yes', 'no']:
                return answer

        if depth > 0 and query.is_question:
            self._interface.output(query.text)
            user_input_text = self._interface.input()
            user_answer = self._qa.ask(query,
                                       f"When asked '{query.text}', the user says: '{user_input_text}'")

            if user_answer.text.lower().replace('.', '') == "yes":
                user_answer = Answer(text="True")

            elif user_input_text.lower().replace('.', '') == "no":
                user_answer = Answer(text="False")

            working_memory.add_story(f"When asked '{query.text}', the user says: '{user_input_text}'")
            if user_answer.text.lower().replace('.', '') != 'unknown':
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
                cause_text = cause.text.strip()
                invert_results = False
                if cause_text[0] == "!":
                    invert_results = True
                    cause_text = cause_text[1:]

                for key, value in substitutions.items():
                    if "(" in cause_text:
                        cause_text = cause_text.replace(" ", "")

                    cause_text = cause_text.replace(key, str(value))

                if cause_text.lower().find("new_frame") == 0:
                    cause_text = cause_text[9:].strip().capitalize()
                    working_memory = WorkingMemory()

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
                            to_execute = add_function_arguments(to_execute)
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
                        new_query,
                        working_memory,
                        depth + 1
                    )

                if invert_results:
                    if answer.text == "False":
                        answer.text = "True"

                    if answer.text == "True":
                        answer.text = "False"

                if answer.text == "False":
                    break

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


def add_function_arguments(text: str) -> str:
    text = re.sub("(.*\([\"'0-9a-zA-Z@\-\.,\s]+)\)$", "\\1, self)", text)
    text = re.sub("(.*)\(\)$", "\\1(self)", text)
    return text
