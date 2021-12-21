import importlib
import logging

from wafl.qa.qa import QA, Answer, Query

_logger = logging.getLogger(__name__)


class BackwardInference:
    def __init__(
        self,
        knowledge: "Knowledge",
        interface: "Interface",
        code_path=None,
        max_depth: int = 4,
    ):
        self._max_depth = max_depth
        self._knowledge = knowledge
        self._interface = interface
        self._qa = QA()
        if code_path:
            self._module = importlib.import_module(f"{code_path}")

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
            user_answer = self._qa.ask(query, f"The user says: {user_input_text}")

            if user_answer.text != "False":
                return user_answer

        rules = self._knowledge.ask_for_rule_backward(query)
        for rule in rules:
            index = 0
            substitutions = {}
            if rule.effect.is_question:
                answer = self._qa.ask(rule.effect, query.text)

                if answer.text == "False":
                    continue

                if answer.variable:
                    substitutions[f"{{{answer.variable.strip()}}}"] = answer.text
                    substitutions[f"({answer.variable.strip()})"] = f'("{answer.text}")'
                    substitutions[f"({answer.variable.strip()},"] = f'("{answer.text}")'
                    substitutions[f",{answer.variable.strip()},"] = f'("{answer.text}")'
                    substitutions[f",{answer.variable.strip()})"] = f'("{answer.text}")'

            for cause in rule.causes:
                new_already_matched = already_matched.copy()

                for key, value in substitutions.items():
                    if "(" in cause.text:
                        cause.text = cause.text.replace(" ", "")

                    cause.text = cause.text.replace(key, value)

                if cause.text.lower().find("say") == 0:
                    utterance = cause.text[3:].strip().capitalize()
                    self._interface.output(utterance)
                    answer = Answer(text="True")

                elif cause.text.lower().find("remember") == 0:
                    utterance = cause.text[8:].strip().capitalize()
                    self._knowledge.add(utterance)
                    answer = Answer(text="True")

                elif "(" in cause.text.lower():
                    if "=" in cause.text:
                        variable, to_execute = cause.text.split("=")
                        variable = variable.strip()
                        to_execute = to_execute.strip()

                    else:
                        to_execute = cause.text.strip()

                    result = eval(f"self._module.{to_execute}")
                    if "=" in cause.text:
                        substitutions.update({f"{{{variable}}}": result})
                        substitutions.update({f"({variable})": result})
                        substitutions.update({f"({variable},": result})
                        substitutions.update({f",{variable},": result})
                        substitutions.update({f",{variable})": result})

                    answer = Answer(text="True")

                else:
                    if "=" in cause.text:
                        variable, text = cause.text.split("=")
                        variable = variable.strip()
                        text = text.strip()
                        new_query = Query(
                            text=text, is_question=True, variable=variable
                        )

                    else:
                        new_query = Query(text=cause.text, is_question=False)

                    answer = self._compute_recursively(
                        new_query, new_already_matched, depth + 1
                    )

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
                    rule.effect.text = rule.effect.text.replace(key, value)

                answer = self._qa.ask(query, rule.effect.text)

                if answer.text == "False":
                    continue

                return answer

        return Answer(text="False")
