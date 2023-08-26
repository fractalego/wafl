import asyncio
import logging
import traceback

from wafl.config import Configuration
from wafl.extractors.code_creator import CodeCreator
from wafl.extractors.task_creator import TaskCreator
from wafl.extractors.task_extractor import TaskExtractor
from wafl.extractors.utils import get_code, get_function_description
from wafl.parsing.rules_parser import get_facts_and_rules_from_text
from wafl.simple_text_processing.questions import is_question, is_yes_no_question
from wafl.events.task_memory import TaskMemory
from wafl.simple_text_processing.deixis import from_bot_to_bot
from wafl.exceptions import InterruptTask, CloseConversation
from wafl.extractors.prompt_predictor import PromptPredictor
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
    update_substitutions_from_answer,
    add_function_arguments,
    invert_answer,
    text_has_assigmnent,
    update_substitutions_from_results,
    answer_is_informative,
    text_is_text_generation_task,
    escape_characters,
    get_causes_list,
    text_has_retrieve_command,
    create_default_substitutions,
)
from wafl.simple_text_processing.normalize import normalized
from wafl.knowledge.utils import needs_substitutions
from wafl.parsing.preprocess import import_module, create_preprocessed
from wafl.extractors.extractor import Extractor
from wafl.extractors.dataclasses import Query, Answer
from inspect import getmembers, isfunction

_logger = logging.getLogger(__name__)


class BackwardInference:
    def __init__(
        self,
        config: "Configuration",
        knowledge: "BaseKnowledge",
        interface: "BaseInterface",
        narrator: "Narrator",
        module_names=None,
        max_depth: int = 3,
        generate_rules: bool = False,
        logger=None,
    ):
        self._max_depth = max_depth
        self._knowledge = knowledge
        self._interface = interface
        self._config = config
        self._extractor = Extractor(config, narrator, logger)
        self._prompt_predictor = PromptPredictor(config, logger)
        self._task_extractor = TaskExtractor(config, interface)
        self._task_creator = TaskCreator(config, knowledge, logger)
        self._code_creator = CodeCreator(config, knowledge)

        self._narrator = narrator
        self._logger = logger
        self._generate_rules = generate_rules
        self._module = {}
        self._functions = {}
        self._sentences_to_utter = []
        if module_names:
            self._init_python_modules(module_names)

    async def get_inference_answer(self, text, policy, task_memory=TaskMemory()):
        query = Query(text=text, is_question=is_question(text))
        knowledge_name = self._knowledge.root_knowledge
        answer = await self._compute_recursively(
            query, task_memory, knowledge_name, policy, depth=1
        )

        if answer.is_true():
            return True

        if answer.is_false():
            return False

        return answer.text

    async def compute(
        self, query, task_memory=None, policy=None, knowledge_name="/", depth=0
    ):
        if query.is_neutral():
            return Answer.create_neutral()

        lock = asyncio.Lock()
        await lock.acquire()
        if not task_memory:
            task_memory = TaskMemory()

        result = await self._compute_recursively(
            query, task_memory, knowledge_name, policy, depth=depth
        )
        lock.release()
        return result

    async def _compute_recursively(
        self,
        query: "Query",
        task_memory,
        knowledge_name,
        policy,
        depth,
        inverted_rule=False,
    ):
        self._log(f"The query is {query.text}", depth)
        self._log(f"The depth is {depth}", depth)
        self._log(f"The max depth is {self._max_depth}", depth)

        if depth == 0:
            answer = await self._look_for_answer_in_rules(
                query, task_memory, knowledge_name, policy, depth, inverted_rule
            )
            if not answer:
                answer = Answer.create_neutral()

            self._log("Answer found by executing the rules: " + answer.text, depth)
            return answer

        if depth > self._max_depth:
            self._log("Max inference depth has been reached: " + str(depth))
            return Answer(text="False")

        candidate_answers = []
        answer = await self._look_for_answer_in_entailment(query, knowledge_name, depth)
        candidate_answers.append(answer)
        if answer and answer_is_informative(answer):
            self._log("Answer in entailment: " + answer.text, depth)
            return answer

        if ":-" in query.text:
            return selected_answer(candidate_answers, query.variable)

        answer = await self._look_for_answer_in_facts(
            query, task_memory, knowledge_name, depth
        )
        candidate_answers.append(answer)
        if answer and not answer.is_neutral():
            self._log("Answers in facts: " + answer.text, depth)
            return answer

        if depth > 0:
            if text_has_new_task_memory_command(query.text):
                task_memory.erase()
                return await self._process_new_task_memory_command()

        answer = await self._look_for_answer_in_last_user_utterance(
            query, task_memory, knowledge_name, depth
        )
        candidate_answers.append(answer)
        if answer and answer_is_informative(answer):
            if not await self._answer_makes_sense(
                query.text, answer.text, self._extractor.get_entailer()
            ):
                answer = Answer.create_neutral(variable=answer.variable)

            self._log("Answers in working memory: " + answer.text, depth)
            return answer

        answer = await self._look_for_answer_in_task_memory(
            query, task_memory, knowledge_name, depth
        )
        candidate_answers.append(answer)
        if answer and answer_is_informative(answer):
            if not await self._answer_makes_sense(
                query.text, answer.text, self._extractor.get_entailer()
            ):
                answer = Answer.create_neutral(variable=answer.variable)

            self._log("Answers in working memory: " + answer.text, depth)
            return answer

        answer = await self._look_for_answer_by_asking_the_user(
            query, task_memory, knowledge_name, policy, depth
        )
        candidate_answers.append(answer)
        if answer and answer_is_informative(answer):
            if not await self._answer_makes_sense(
                query.text, answer.text, self._extractor.get_entailer()
            ):
                answer = Answer.create_neutral(variable=answer.variable)

            self._log("Answers by asking the user: " + answer.text, depth)
            return answer

        if depth > 0:
            task_memory = TaskMemory()
            if text_has_say_command(query.text):
                answer = await self._process_say_command(query.text)
                return answer

            elif text_has_remember_command(query.text):
                return await self._process_remember_command(query.text, knowledge_name)

            elif text_is_code(query.text):
                return await self._process_code(
                    query.text, "", knowledge_name, {}, policy
                )

        answer = await self._look_for_answer_in_rules(
            query, task_memory, knowledge_name, policy, depth, inverted_rule
        )
        candidate_answers.append(answer)
        if answer and answer_is_informative(answer):
            self._log("Answer found by executing the rules: " + answer.text, depth)
            return answer

        return selected_answer(candidate_answers, query.variable)

    async def _look_for_answer_in_rules(
        self, query, task_memory, query_knowledge_name, policy, depth, inverted_rule
    ):
        self._log(f"Looking for answers in rules")
        rules = await self._knowledge.ask_for_rule_backward(
            query, knowledge_name=query_knowledge_name
        )
        if not rules and self._generate_rules:
            self._log(f"Creating rules for the task: {query.text}", depth)
            rules_answer = await self._task_creator.extract(query.text)
            if not rules_answer.is_neutral():
                rules = get_facts_and_rules_from_text(
                    rules_answer.text, query_knowledge_name
                )["rules"]

            for rule in rules:
                await self._interface.add_choice(f"The bot created the rule:")
                await self._interface.add_choice(str(rule))

        for rule in rules:
            index = 0
            substitutions = create_default_substitutions(self._interface)
            rule_effect_text = rule.effect.text
            knowledge_name = rule.knowledge_name
            self._log(f"Trying rule with trigger: {rule_effect_text}", depth)
            if is_question(rule_effect_text):
                if not await self._validate_question_in_effects(
                    rule.effect, query.text, substitutions
                ):
                    continue

            elif not needs_substitutions(rule.effect):
                answer = await self._validate_fact_in_effects(
                    rule_effect_text, query, substitutions
                )
                if answer.is_false():
                    continue

            if (
                not rule.effect.is_interruption
                and policy
                and not await policy.accept(f"The bot understands '{rule_effect_text}'")
            ):
                continue

            await self._interface.add_choice(
                f"The bot selected the rule with trigger {rule_effect_text}."
            )

            for cause in rule.causes:
                cause_text = cause.text.strip()
                self._log("clause: " + cause_text, depth)
                original_cause_text = cause_text
                if task_memory.is_in_prior_failed_clauses(original_cause_text):
                    self._log("This clause failed before", depth)
                    break

                code_description = ""
                if text_is_code(cause_text):
                    code_description = get_function_description(cause_text)
                    cause_text = get_code(cause_text)

                cause_text = apply_substitutions(cause_text, substitutions)
                if code_description:
                    apply_substitutions(code_description, substitutions)

                cause_text, invert_results = check_negation(cause_text)
                cause_text_list = get_causes_list(cause_text)

                answers = []
                for cause_text in cause_text_list:
                    answer = await self._process_cause(
                        cause_text,
                        cause.is_question,
                        code_description,
                        knowledge_name,
                        substitutions,
                        policy,
                        task_memory,
                        depth,
                        invert_results,
                    )
                    if type(answer) == list:
                        answers.extend(answer)

                    else:
                        answers.append(answer)

                if len(answers) > 1:
                    answer = Answer.create_from_text(
                        str([item.text for item in answers])[1:-1]
                    )

                else:
                    answer = answers[0]

                if answers:
                    answer.variable = answers[0].variable

                if invert_results:
                    answer = invert_answer(answer)

                if answer.is_false():
                    task_memory.add_failed_clause(original_cause_text)
                    break

                if answer.variable:
                    update_substitutions_from_answer(answer, substitutions)

                if depth == 0:
                    await self._flush_interface_output()

                index += 1

            if index == len(rule.causes):
                answer = await self._validate_fact_in_effects(
                    rule_effect_text, query, substitutions
                )
                if answer.is_neutral():
                    return answer.create_true()

                if not answer.is_false():
                    return answer

            if inverted_rule:
                return Answer(text="False")

    async def _process_cause(
        self,
        cause_text,
        cause_is_question,
        code_description,
        knowledge_name,
        substitutions,
        policy,
        task_memory,
        depth,
        invert_results,
    ):
        if text_has_say_command(cause_text):
            answer = await self._process_say_command(cause_text)

        elif text_has_retrieve_command(cause_text):
            answer = await self._process_retrieve_command(cause_text)

        elif text_has_remember_command(cause_text):
            answer = await self._process_remember_command(cause_text, knowledge_name)

        elif text_is_code(cause_text):
            answer = await self._process_code(
                cause_text,
                code_description,
                knowledge_name,
                substitutions,
                policy,
            )

        elif await text_is_text_generation_task(
            cause_text, self._extractor.get_entailer()
        ):
            answer = await self._process_text_generation(
                cause_text, knowledge_name, substitutions
            )

        else:
            answer = await self._process_query(
                cause_text,
                cause_is_question,
                task_memory,
                knowledge_name,
                policy,
                depth,
                inverted_rule=invert_results,
            )
            if answer.is_neutral() and answer.variable:
                answer = Answer.create_false()

        return answer

    async def _look_for_answer_in_facts(
        self, query, task_memory, knowledge_name, depth
    ):
        self._log(f"Looking for answers in facts")
        facts_and_thresholds = await self._knowledge.ask_for_facts_with_threshold(
            query, is_from_user=depth == 0, knowledge_name=knowledge_name
        )
        texts = cluster_facts(facts_and_thresholds)
        for text in texts:
            self._log(f"Answer within facts: The query is {query.text}")
            self._log(f"Answer within facts: The context is {text}")
            text = self._narrator.get_context_for_facts(text)
            answer = await self._extractor.extract(query, text)
            task_memory.add_story(text)
            self._log(f"Answer within facts: The answer is {answer.text}")
            return answer

    async def _look_for_answer_in_entailment(self, query, knowledge_name, depth):
        self._log(f"Looking for answers in entailment")
        if ":-" not in query.text:
            return None

        hypothesis, premise = query.text.split(":-")
        answer = await self._extractor.extract(
            Query(text=premise, is_question=is_question(premise)), hypothesis
        )
        return answer

    async def _look_for_answer_in_last_user_utterance(
        self, query, task_memory, knowledge_name, depth
    ):
        self._log(f"Looking for answers in the user's last utterance")
        if depth > 0 and task_memory.get_story() and query.is_question:
            query.text = from_bot_to_bot(query.text)
            user_utterances = [
                item.replace("user:", "The user says:")
                for item in self._interface.get_utterances_list()
                if "user:" in item
            ]
            if not user_utterances:
                return None

            answer = await self._extractor.extract(
                query, user_utterances[-1], task_memory
            )
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

    async def _look_for_answer_in_task_memory(
        self, query, task_memory, knowledge_name, depth
    ):
        self._log(f"Looking for answers in task memory")
        if depth > 0 and task_memory.get_story() and query.is_question:
            query.text = from_bot_to_bot(query.text)
            answer = await self._extractor.extract(
                query, task_memory.get_story(), task_memory
            )
            if task_memory.text_is_in_prior_questions(answer.text):
                answer.text = "unknown"

            if (
                not answer.is_true()
                and not answer.is_false()
                and task_memory.text_is_in_prior_answers(answer.text)
            ):
                answer.text = "unknown"

            task_memory.add_answer(answer.text)

            if not query.is_question:
                return answer

            if answer.text[-1] == ".":
                answer.text = answer.text[:-1]

            return answer

    async def _look_for_answer_by_asking_the_user(
        self, query, task_memory, knowledge_name, policy, depth
    ):
        self._log(f"Looking for answers by asking the user")
        if depth > 0 and query.is_question:
            await self._flush_interface_output()
            while True:
                self._log(f"Asking the user: {query.text}")
                await self._interface.output(query.text)
                user_input_text = await self._interface.input()
                self._log(f"The user replies: {user_input_text}")
                if await self._query_has_better_match(query.text, user_input_text):
                    self._log(f"Found a better match for {user_input_text}", depth)
                    task_text = (
                        await self._task_extractor.extract(user_input_text)
                    ).text
                    await self._interface.add_choice(
                        f"The bot tries to see if the new task can be '{task_text}'"
                    )
                    await self._spin_up_another_inference_task(
                        user_input_text,
                        task_memory,
                        knowledge_name,
                        policy,
                        depth,
                    )
                    await self._interface.add_choice(
                        f"The task '{task_text}' did not bring any result."
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
                user_answer = await self._extractor.extract(query, story)

                self._log(f"The answer that is understood: {user_answer.text}")

                if is_yes_no_question(query.text):
                    user_answer = project_answer(user_answer, ["yes", "no"])
                    if user_answer.text not in ["yes", "no"]:
                        await self._interface.output("Yes or No?")
                        user_answer = await self._look_for_answer_by_asking_the_user(
                            query, task_memory, knowledge_name, policy, depth
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

    async def _validate_question_in_effects(self, effect, query_text, substitutions):
        answer = await self._extractor.extract(effect, query_text)
        self._log("Validating question in the rule trigger.")
        self._log(f"The query is {query_text}")
        self._log(f"The answer is {answer.text}")

        if answer.is_false() or not answer_is_informative(answer):
            return False

        if answer.variable:
            update_substitutions_from_answer(answer, substitutions)

        return True

    async def _process_say_command(self, cause_text):
        utterance = cause_text.strip()[3:].strip().capitalize()
        self._log(f"Uttering: {utterance}")
        self._sentences_to_utter.append(utterance)
        answer = Answer.create_true()
        return answer

    async def _process_remember_command(self, cause_text, knowledge_name):
        utterance = cause_text[8:].strip()
        if ":-" in utterance:
            self._log(
                f"Adding the following Rule to the knowledge name {knowledge_name}: {utterance}"
            )
            await self._knowledge.add_rule(utterance, knowledge_name=knowledge_name)

        else:
            self._log(
                f"Adding the following Fact to the knowledge name {knowledge_name}: {utterance}"
            )
            await self._knowledge.add(utterance, knowledge_name=knowledge_name)

        return Answer(text="True")

    async def _process_new_task_memory_command(self):
        self._log(f"Erasing working memory")
        return Answer(text="True")

    async def _validate_fact_in_effects(self, rule_effect_text, query, substitutions):
        for key, value in substitutions.items():
            if key and value:
                rule_effect_text = rule_effect_text.replace(key, value)

        answer = await self._extractor.extract(query, rule_effect_text)
        self._log("Validating the statement in the rule trigger.")
        self._log(f"The query is {rule_effect_text}")
        self._log(f"The answer is {answer.text}")
        return answer

    async def _process_code(
        self, cause_text, code_description, knowledge_name, substitutions, policy
    ):
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

            task_memory = (
                TaskMemory()
            )  # task_memory is used as argument of the code in eval()
            to_execute = escape_characters(to_execute)
            self._log(f"Executing code: {to_execute}")

            if not code_description:
                result = eval(f"self._module['{knowledge_name}'].{to_execute}")
                if result is not None:
                    result = await result

            else:
                generated_function_answer = await self._code_creator.extract(
                    cause_text + f" <{code_description}>"
                )
                exec(generated_function_answer.text)
                result = eval(to_execute)

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

    async def _process_text_generation(self, cause_text, knowledge_name, substitutions):
        if "=" not in cause_text:
            return Answer(text="False")

        position_of_assignment_operator = cause_text.find("=")
        variable, prompt = (
            cause_text[:position_of_assignment_operator].strip(),
            cause_text[position_of_assignment_operator + 1 :].strip(),
        )
        variable = variable.strip()
        prompt = prompt.strip()
        answer = await self._prompt_predictor.predict(prompt)
        answer.variable = variable
        update_substitutions_from_results(answer.text, variable, substitutions)
        return answer

    async def _process_query(
        self,
        cause_text,
        cause_is_question,
        task_memory,
        knowledge_name,
        policy,
        depth,
        inverted_rule,
    ):
        if "=" in cause_text:
            variable, text = cause_text.split("=")
            variable = variable.strip()
            text = text.strip()
            new_query = Query(
                text=text, is_question=is_question(text), variable=variable
            )

        elif cause_is_question:
            new_query = Query(text=cause_text, is_question=True)

        else:
            new_query = Query(text=cause_text, is_question=False)

        additional_text = ""
        if inverted_rule:
            additional_text = "NOT "

        await self._interface.add_choice(
            f"The bot tries the new query '{additional_text + new_query.text}'"
        )
        answer = await self._compute_recursively(
            new_query, task_memory, knowledge_name, policy, depth + 1, inverted_rule
        )
        self._log(f"The answer to the query is {answer.text}", depth)

        if answer.variable and answer.is_neutral():
            return Answer(text="False", variable=answer.variable)

        if not new_query.variable:
            await self._flush_interface_output()

        elif self._sentences_to_utter:
            answer.text = "\n".join(self._sentences_to_utter)
            self._sentences_to_utter = []

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

    async def _spin_up_another_inference_task(
        self, input_text, task_memory, knowledge_name, policy, depth
    ):
        prior_conversation = self._narrator.summarize_dialogue()
        working_memory = TaskMemory()
        working_memory.add_story(prior_conversation)
        query_text = f"The user says: '{input_text}.'"
        working_memory.add_story(query_text)
        query = Query(
            text=query_text,
            is_question=is_question(query_text),
            variable="name",
        )
        self._interface.bot_has_spoken(False)
        self._log(f"Spinning up another inference task", depth)
        await self._compute_recursively(
            query,
            task_memory,
            knowledge_name,
            policy,
            depth,
        )
        await self._flush_interface_output()

    async def _flush_interface_output(self):
        for _ in range(len(self._sentences_to_utter)):
            await self._interface.output(self._sentences_to_utter.pop(0))

    async def _process_retrieve_command(self, cause_text):
        cause_text = cause_text.replace("retrieve", "")
        cause_text = cause_text.replace("RETRIEVE", "")
        if "=" in cause_text:
            variable, text = cause_text.split("=")
            variable = variable.strip()
            text = text.strip()
            query = Query(text=text, is_question=is_question(text), variable=variable)

        else:
            variable = None
            query = Query(text=cause_text, is_question=is_question(cause_text))

        facts = await self._knowledge.ask_for_facts_with_threshold(query, threshold=0.5)
        return [Answer(text=item[0].text, variable=variable) for item in facts]

    async def _query_has_better_match(
        self,
        query: str,
        user_answer: str,
    ):
        if is_question(user_answer):
            return True

        if await self._knowledge.has_better_match(user_answer):
            return True

        return False

    async def _answer_makes_sense(
        self, query: str, user_answer: str, entailer: "Entailer"
    ):
        result = await entailer.entails(
            f"bot: {query} user: {user_answer}",
            "the user refuses to answer",
            threshold=0.9,
            return_threshold=True,
        )
        if result:
            return False

        result = await entailer.entails(
            f"bot: {query} user: {user_answer}",
            "The answer gives no information",
            threshold=0.9,
            return_threshold=True,
        )
        if result:
            return False

        return True
