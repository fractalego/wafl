import logging
import traceback

from wafl.answerer.inference_answerer import get_answer_using_text
from wafl.conversation.utils import (
    is_question,
    is_yes_no_question,
)
from wafl.conversation.task_memory import TaskMemory
from wafl.deixis import from_bot_to_bot
from wafl.exceptions import InterruptTask, CloseConversation
from wafl.inference.utils import (
    cluster_facts,
    selected_answer,
    project_answer,
    text_has_new_task_memory_command,
    text_has_say_command,
    text_has_remember_command,
    text_is_code,
    check_negation,
    apply_substitutions,
    normalized,
    update_substitutions_from_answer,
    add_function_arguments,
    invert_answer,
    text_has_assigmnent,
    update_substitutions_from_results,
    answer_is_informative,
)
from wafl.knowledge.utils import needs_substitutions
from wafl.parsing.preprocess import import_module, create_preprocessed
from wafl.qa.qa import QA
from wafl.qa.dataclasses import Query, Answer
from inspect import getmembers, isfunction

_logger = logging.getLogger(__name__)


class BackwardInference:
    def __init__(
        self,
        knowledge: "BaseKnowledge",
        interface: "BaseInterface",
        narrator: "Narrator",
        module_names=None,
        max_depth: int = 10,
        logger=None,
    ):
        self._max_depth = max_depth
        self._knowledge = knowledge
        self._interface = interface
        self._qa = QA(narrator, logger)
        self._narrator = narrator
        self._logger = logger
        self._module = {}
        self._functions = {}
        if module_names:
            self._init_python_modules(module_names)

    def get_inference_answer(self, text, task_memory=TaskMemory()):
        query = Query(text=text, is_question=is_question(text))
        knowledge_name = self._knowledge.root_knowledge
        answer = self._compute_recursively(query, task_memory, knowledge_name, depth=1)

        if answer.is_true():
            return True

        if answer.is_false():
            return False

        return answer.text

    def compute(self, query, task_memory=None, knowledge_name="/"):
        if not task_memory:
            task_memory = TaskMemory()

        return self._compute_recursively(query, task_memory, knowledge_name, depth=0)

    def _compute_recursively(
        self, query: "Query", task_memory, knowledge_name, depth, inverted_rule=False
    ):
        self._log(f"The query is {query.text}", depth)
        self._log(f"The depth is {depth}", depth)
        self._log(f"The max depth is {self._max_depth}", depth)

        if depth > self._max_depth:
            return Answer(text="False")

        candidate_answers = []
        answer = self._look_for_answer_in_entailment(query, knowledge_name, depth)
        candidate_answers.append(answer)
        if answer and answer_is_informative(answer):
            self._log("Answer in entailment: " + answer.text, depth)
            return answer

        if " -> " in query.text:
            return selected_answer(candidate_answers)

        answer = self._look_for_answer_in_facts(
            query, task_memory, knowledge_name, depth
        )
        candidate_answers.append(answer)
        if answer and not answer.is_neutral():
            self._log("Answers in facts: " + answer.text, depth)
            return answer

        if depth > 0:
            if text_has_new_task_memory_command(query.text):
                task_memory.erase()
                return self._process_new_task_memory_command()

        answer = self._look_for_answer_in_task_memory(
            query, task_memory, knowledge_name, depth
        )
        candidate_answers.append(answer)
        if answer and answer_is_informative(answer):
            self._log("Answers in working memory: " + answer.text, depth)
            return answer

        answer = self._look_for_answer_by_asking_the_user(
            query, task_memory, knowledge_name, depth
        )
        candidate_answers.append(answer)
        if answer and answer_is_informative(answer):
            self._log("Answers by asking the user: " + answer.text, depth)
            return answer

        if depth > 0:
            task_memory = TaskMemory()
            if text_has_say_command(query.text):
                answer = self._process_say_command(query.text)
                return answer

            elif text_has_remember_command(query.text):
                return self._process_remember_command(query.text, knowledge_name)

            elif text_is_code(query.text):
                return self._process_code(query.text, knowledge_name, {})

        answer = self._look_for_answer_in_rules(
            query, task_memory, knowledge_name, depth, inverted_rule
        )
        candidate_answers.append(answer)
        if answer and answer_is_informative(answer):
            self._log("Answer found by executing the rules: " + answer.text, depth)
            return answer

        return selected_answer(candidate_answers)

    def _look_for_answer_in_rules(
        self, query, task_memory, query_knowledge_name, depth, inverted_rule
    ):
        rules = self._knowledge.ask_for_rule_backward(
            query, knowledge_name=query_knowledge_name
        )
        for rule in rules:
            index = 0
            substitutions = {}

            rule_effect_text = rule.effect.text
            knowledge_name = rule.knowledge_name
            self._log(f"Trying rule with trigger: {rule_effect_text}", depth)
            if rule.effect.is_question:
                if not self._validate_question_in_effects(
                    rule.effect, query.text, substitutions
                ):
                    continue

            elif not needs_substitutions(rule.effect):
                answer = self._validate_fact_in_effects(
                    rule_effect_text, query, substitutions
                )
                if answer.is_false():
                    continue

            for cause in rule.causes:
                cause_text = cause.text.strip()
                self._log("clause: " + cause_text, depth)
                cause_text, invert_results = check_negation(cause_text)
                cause_text = apply_substitutions(cause_text, substitutions)
                if task_memory.is_in_prior_failed_clauses(cause_text):
                    self._log("This clause failed before", depth)
                    continue

                if text_has_say_command(cause_text):
                    answer = self._process_say_command(cause_text)

                elif text_has_remember_command(cause_text):
                    answer = self._process_remember_command(cause_text, knowledge_name)

                elif text_is_code(cause_text):
                    answer = self._process_code(
                        cause_text, knowledge_name, substitutions
                    )

                else:
                    answer = self._process_query(
                        cause_text,
                        cause.is_question,
                        task_memory,
                        knowledge_name,
                        depth,
                        inverted_rule=invert_results,
                    )

                if invert_results:
                    answer = invert_answer(answer)

                if answer.is_false():
                    task_memory.add_failed_clause(cause_text)
                    break

                if answer.variable:
                    update_substitutions_from_answer(answer, substitutions)

                index += 1

            if index == len(rule.causes):
                answer = self._validate_fact_in_effects(
                    rule_effect_text, query, substitutions
                )

                if not answer.is_false():
                    return answer

            if inverted_rule:
                return Answer(text="False")

    def _look_for_answer_in_facts(self, query, task_memory, knowledge_name, depth):
        facts_and_thresholds = self._knowledge.ask_for_facts_with_threshold(
            query, is_from_user=depth == 0, knowledge_name=knowledge_name
        )
        texts = cluster_facts(facts_and_thresholds)
        for text in texts:
            self._log(f"Answer within facts: The query is {query.text}")
            self._log(f"Answer within facts: The context is {text}")
            text = self._narrator.get_context_for_facts(text)
            answer = self._qa.ask(query, text)
            task_memory.add_story(text)
            self._log(f"Answer within facts: The answer is {answer.text}")
            return answer

    def _look_for_answer_in_entailment(self, query, knowledge_name, depth):
        if "->" not in query.text:
            return None

        premise, hypothesis = query.text.split("->")
        answer = self._qa.ask(
            Query(text=premise, is_question=is_question(premise)), hypothesis
        )
        return answer

    def _look_for_answer_in_task_memory(
        self, query, task_memory, knowledge_name, depth
    ):
        if depth > 0 and task_memory.get_story() and query.is_question:
            query.text = from_bot_to_bot(query.text)
            answer = self._qa.ask(query, task_memory.get_story(), task_memory)
            if task_memory.text_is_in_prior_questions(answer.text):
                answer.text = "unknown"

            if task_memory.text_is_in_prior_answers(answer.text):
                answer.text = "unknown"

            task_memory.add_answer(answer.text)

            if not query.is_question:
                return answer

            if normalized(answer.text) not in [
                "unknown",
                "yes",
                "no",
            ]:
                if answer.text[-1] == ".":
                    answer.text = answer.text[:-1]

                return answer

    def _look_for_answer_by_asking_the_user(
        self, query, task_memory, knowledge_name, depth
    ):
        if depth > 0 and query.is_question:

            while True:
                self._log(f"Asking the user: {query.text}")
                self._interface.output(query.text)
                user_input_text = self._interface.input()
                self._log(f"The user replies: {user_input_text}")
                if self._knowledge.has_better_match(user_input_text):
                    prior_conversation = self._narrator.summarize_dialogue()
                    get_answer_using_text(
                        self, self._interface, user_input_text, prior_conversation
                    )

                else:
                    break

            if normalized(user_input_text) == "yes":
                user_answer = Answer(text="True")

            elif normalized(user_input_text) == "no":
                user_answer = Answer(text="False")

            else:
                story = (
                    f"When asked '{query.text}', the user says: '{user_input_text}.'"
                )
                query.text = from_bot_to_bot(query.text)
                user_answer = self._qa.ask(query, story)

                self._log(f"The answer that is understood: {user_answer.text}")

                if is_yes_no_question(query.text):
                    user_answer = project_answer(user_answer, ["yes", "no"])
                    if user_answer.text not in ["yes", "no"]:
                        self._interface.output("Yes or No?")
                        user_answer = self._look_for_answer_by_asking_the_user(
                            query, task_memory, knowledge_name, depth
                        )

                if user_answer.is_true():
                    user_answer = Answer(text="True")
                    task_memory.add_story(story)
                    task_memory.add_question(query.text)
                    task_memory.add_answer("yes")

                elif user_answer.is_false():
                    user_answer = Answer(text="False")

                else:
                    task_memory.add_story(story)
                    task_memory.add_question(query.text)
                    task_memory.add_answer(user_input_text)

            if not user_answer.is_neutral():
                if user_answer.text[-1] == ".":
                    user_answer.text = user_answer.text[:-1]
                return user_answer

    def _validate_question_in_effects(self, effect, query_text, substitutions):
        answer = self._qa.ask(effect, query_text)
        self._log("Validating question in the rule trigger.")
        self._log(f"The query is {query_text}")
        self._log(f"The answer is {answer.text}")

        if answer.is_false() or not answer_is_informative(answer):
            return False

        if answer.variable:
            update_substitutions_from_answer(answer, substitutions)

        return True

    def _process_say_command(self, cause_text):
        utterance = cause_text.strip()[3:].strip().capitalize()
        self._log(f"Uttering: {utterance}")
        self._interface.output(utterance)
        answer = Answer(text="True")
        return answer

    def _process_remember_command(self, cause_text, knowledge_name):
        utterance = cause_text[8:].strip().capitalize()
        self._log(f"Remembering: {utterance}")
        self._knowledge.add(utterance, knowledge_name=knowledge_name)
        return Answer(text="True")

    def _process_new_task_memory_command(self):
        self._log(f"Erasing working memory")
        return Answer(text="True")

    def _validate_fact_in_effects(self, rule_effect_text, query, substitutions):
        for key, value in substitutions.items():
            if key and value:
                rule_effect_text = rule_effect_text.replace(key, value)

        answer = self._qa.ask(query, rule_effect_text)
        self._log("Validating the statement in the rule trigger.")
        self._log(f"The query is {rule_effect_text}")
        self._log(f"The answer is {answer.text}")

        if answer.is_true():
            return answer

        return answer

    def _process_code(self, cause_text, knowledge_name, substitutions):
        variable = None
        if "=" in cause_text:
            variable, to_execute = cause_text.split("=")
            variable = variable.strip()
            to_execute = to_execute.strip()

        else:
            to_execute = cause_text.strip()

        try:
            if any(
                item + "(" in to_execute for item in self._functions[knowledge_name]
            ):
                to_execute = add_function_arguments(to_execute)

            task_memory = TaskMemory()
            self._log(f"Executing code: {to_execute}")
            # task_memory is used as argument of the code in eval()
            result = eval(f"self._module['{knowledge_name}'].{to_execute}")
            self._log(f"Execution result: {result}")

        except (CloseConversation, InterruptTask) as e:
            _logger.warning(str(e))
            raise e

        except Exception as e:
            traceback.print_exc()
            _logger.warning(str(e))
            result = False

        if text_has_assigmnent(cause_text) and variable:
            update_substitutions_from_results(result, variable, substitutions)

        if result != False:
            answer = Answer(text=str(result))

        else:
            answer = Answer(text="False")

        return answer

    def _process_query(
        self,
        cause_text,
        cause_is_question,
        task_memory,
        knowledge_name,
        depth,
        inverted_rule,
    ):
        self._log("Processing clause as a query", depth)
        if "=" in cause_text:
            variable, text = cause_text.split("=")
            variable = variable.strip()
            text = text.strip()
            new_query = Query(text=text, is_question=True, variable=variable)

        elif cause_is_question:
            new_query = Query(text=cause_text, is_question=True)

        else:
            new_query = Query(text=cause_text, is_question=False)

        answer = self._compute_recursively(
            new_query, task_memory, knowledge_name, depth + 1, inverted_rule
        )
        self._log(f"The answer to the query is {answer.text}", depth)
        return answer

    def _log(self, text, depth=None):
        if self._logger:
            if depth:
                self._logger.set_depth(depth)

            self._logger.write(f"BackwardInference: {text}", self._logger.level.INFO)

    def _init_python_modules(self, module_names):
        if type(module_names) == str:
            module_names = [module_names]

        for module_name in module_names:
            create_preprocessed(module_name)
            self._module[module_name] = import_module(module_name)
            self._functions[module_name] = [
                item[0] for item in getmembers(self._module[module_name], isfunction)
            ]
