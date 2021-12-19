import logging

from wafl.facts import Fact
from wafl.qa.qa import QA, Answer, Query

_logger = logging.getLogger(__name__)


class BackwardInference:

    def __init__(self, knowledge: "Knowledge", max_depth: int = 4):
        self._max_depth = max_depth
        self._knowledge = knowledge
        self._qa = QA()

    def compute(self, query):
        return self._compute_recursively(query, already_matched=set(), depth=0)

    def _compute_recursively(self, query: "Query", already_matched, depth):
        if depth > self._max_depth:
            return Answer(text='False')

        facts = self._knowledge.ask_for_facts(query.text)
        for fact in facts:
            answer = self._qa.ask(query, fact.text)
            if str(fact) in already_matched:
                continue

            #already_matched.add(str(fact)) ### THIS IS MORE COMPLICATED THEN PROLOG
            return answer

        rules = self._knowledge.ask_for_rule_backward(query.text)
        for rule in rules:
            index = 0
            substitutions = {}
            for cause in rule.causes:
                new_already_matched = already_matched.copy()

                for key, value in substitutions.items():
                    cause = cause.replace(key, value)

                if cause.lower().find('say') == 0:
                    answer = Answer(text='True')

                else:
                    if '?' in cause:
                        text, variable = cause.split('?')
                        new_query = Query(text=text, is_question=True, variable=variable)

                    else:
                        new_query = Query(text=cause, is_question=False)

                    answer = self._compute_recursively(new_query, new_already_matched, depth + 1)

                if answer.text == 'False':
                    break

                already_matched = new_already_matched
                if answer.variable:
                     substitutions[f'{{{answer.variable.strip()}}}'] = answer.text
                index += 1

            if index == len(rule.causes):
                return Answer(text='True')

        return Answer(text='False')
