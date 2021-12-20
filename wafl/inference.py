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

        facts = self._knowledge.ask_for_facts(query)
        for fact in facts:
            answer = self._qa.ask(query, fact.text)
            if str(fact) in already_matched:
                continue

            #already_matched.add(str(fact)) ### THIS IS MORE COMPLICATED THEN PROLOG
            return answer

        rules = self._knowledge.ask_for_rule_backward(query)
        for rule in rules:
            index = 0
            substitutions = {}
            answer = self._qa.ask(rule.effect, query.text)
            if answer.text == 'False':
                continue

            if answer.variable:
                 substitutions[f'{{{answer.variable.strip()}}}'] = answer.text

            for cause in rule.causes:
                new_already_matched = already_matched.copy()

                for key, value in substitutions.items():
                    cause.text = cause.text.replace(key, value)

                if cause.text.lower().find('say') == 0:
                    answer = Answer(text='True')

                else:
                    if '?' in cause.text:
                        text, variable = cause.text.split('?')
                        new_query = Query(text=text, is_question=True, variable=variable)

                    else:
                        new_query = Query(text=cause.text, is_question=False)

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
