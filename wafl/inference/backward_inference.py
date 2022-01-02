import logging
import traceback

from wafl.conversation.utils import is_question
from wafl.conversation.working_memory import WorkingMemory
from wafl.inference.utils import (
    check_negation,
    text_is_code,
    apply_substitutions,
    text_has_say_command,
    text_has_remember_command,
    update_substitutions_from_answer,
    add_function_arguments,
    update_substitutions_from_results,
    invert_answer,
    text_has_assigmnent,
)
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

    def _compute_recursively(self, query: "Query", working_memory, depth):
        if depth > self._max_depth:
            return Answer(text="False")

        answer = self._look_for_answer_in_facts(query, working_memory)
        if answer:
            return answer

        answer = self._look_for_answer_in_working_memory(query, working_memory, depth)
        if answer:
            return answer

        answer = self._look_for_answer_by_asking_the_user(query, working_memory, depth)
        if answer:
            return answer

        answer = self._look_for_answer_in_rules(query, working_memory, depth)
        if answer:
            return answer

        return Answer(text="False")

    def _look_for_answer_in_rules(self, query, working_memory, depth):
        rules = self._knowledge.ask_for_rule_backward(query)
        for rule in rules:
            index = 0
            substitutions = {}
            bot_has_spoken = False

            rule_effect_text = rule.effect.text

            if rule.effect.is_question:
                self._validate_question_in_effects(
                    rule.effect, query.text, substitutions
                )

            for cause in rule.causes:
                cause_text = cause.text.strip()
                cause_text, invert_results = check_negation(cause_text)
                cause_text = apply_substitutions(cause_text, substitutions)

                if text_has_say_command(cause_text):
                    answer, bot_has_spoken = self.__process_say_command(cause_text)

                elif text_has_remember_command(cause_text):
                    answer = self.__process_remember_command(cause_text)

                elif text_is_code(cause_text):
                    answer = self.__process_code(cause_text, substitutions)

                else:
                    answer = self.__process_query(
                        cause_text, cause.is_question, working_memory, depth
                    )

                if invert_results:
                    answer = invert_answer(answer)

                if answer.text == "False":
                    break

                if answer.variable:
                    update_substitutions_from_answer(answer, substitutions)

                index += 1

            if index == len(rule.causes):
                answer = self.__validate_fact_in_effects(
                    rule_effect_text, query, substitutions, bot_has_spoken
                )
                if answer:
                    return answer

    def _look_for_answer_in_facts(self, query, working_memory):
        facts = self._knowledge.ask_for_facts(query)
        for fact in facts:
            answer = self._qa.ask(query, fact.text)

            working_memory.add_story(fact.text)
            return answer

    def _look_for_answer_in_working_memory(self, query, working_memory, depth):
        if query.is_question and depth > 0 and working_memory.get_story():
            answer = self._qa.ask(query, working_memory.get_story())
            if answer.text.lower().replace(".", "") not in ["unknown", "yes", "no"]:
                return answer

    def _look_for_answer_by_asking_the_user(self, query, working_memory, depth):
        if depth > 0 and query.is_question:
            self._interface.output(query.text)
            user_input_text = self._interface.input()
            working_memory.add_story(
                f"When asked '{query.text}', the user says: '{user_input_text}'"
            )

            if user_input_text.lower().replace(".", "") == "yes":
                user_answer = Answer(text="True")

            elif user_input_text.lower().replace(".", "") == "no":
                user_answer = Answer(text="False")

            else:
                user_answer = self._qa.ask(
                    query,
                    f"When asked '{query.text}', the user says: '{user_input_text}'",
                )

                if user_answer.text.lower().replace(".", "") == "yes":
                    user_answer = Answer(text="True")

                elif user_answer.text.lower().replace(".", "") == "no":
                    user_answer = Answer(text="False")

            if user_answer.text.lower().replace(".", "") != "unknown":
                return user_answer

    def _validate_question_in_effects(self, effect, query_text, substitutions):
        answer = self._qa.ask(effect, query_text)

        if answer.text == "False":
            return False

        if answer.variable:
            update_substitutions_from_answer(answer, substitutions)

        return True

    def __process_say_command(self, cause_text):
        utterance = cause_text[3:].strip().capitalize()
        self._interface.output(utterance)
        bot_has_spoken = True
        answer = Answer(text="True")
        return answer, bot_has_spoken

    def __process_remember_command(self, cause_text):
        utterance = cause_text[8:].strip().capitalize()
        self._knowledge.add(utterance)
        return Answer(text="True")

    def __validate_fact_in_effects(
        self, rule_effect_text, query, substitutions, bot_has_spoken
    ):
        for key, value in substitutions.items():
            rule_effect_text = rule_effect_text.replace(key, value)

        answer = self._qa.ask(query, rule_effect_text)

        if answer.text == "False":
            return False

        if answer.text.lower() == "yes" or bot_has_spoken:
            answer.text = "True"

        return answer

    def __process_code(self, cause_text, substitutions):
        variable = None
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

        if text_has_assigmnent(cause_text) and variable:
            update_substitutions_from_results(result, variable, substitutions)

        if result != False:
            answer = Answer(text="True")

        else:
            answer = Answer(text="False")

        return answer

    def __process_query(self, cause_text, cause_is_question, working_memory, depth):
        if "=" in cause_text:
            variable, text = cause_text.split("=")
            variable = variable.strip()
            text = text.strip()
            new_query = Query(text=text, is_question=True, variable=variable)

        elif cause_is_question:
            new_query = Query(text=cause_text, is_question=True)

        else:
            new_query = Query(text=cause_text, is_question=False)

        answer = self._compute_recursively(new_query, working_memory, depth + 1)

        return answer
