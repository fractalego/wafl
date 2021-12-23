import logging

from wafl.facts import Fact
from wafl.knowledge.base_knowledge import BaseKnowledge
from wafl.parser import get_facts_and_rules_from_text
from wafl.retriever import Retriever
from wafl.text_utils import clean_text_for_retrieval

_logger = logging.getLogger(__name__)


class Knowledge(BaseKnowledge):
    _threshold_for_questions = 0.51
    _threshold_for_questions_in_rules = 0.49
    _threshold_for_facts = 0.58
    _threshold_for_partial_facts = 0.42

    def __init__(self, rules_text=None):
        facts_and_rules = get_facts_and_rules_from_text(rules_text)
        self._facts_dict = {
            f"F{index}": value for index, value in enumerate(facts_and_rules["facts"])
        }
        self._rules_dict = {
            f"R{index}": value for index, value in enumerate(facts_and_rules["rules"])
        }
        self._facts_retriever = Retriever()
        self._rules_incomplete_retriever = Retriever()
        self._rules_fact_retriever = Retriever()
        self._rules_question_retriever = Retriever()
        self._initialize_retrievers()

    def add(self, text):
        fact_index = f"F{len(self._facts_dict)}"
        self._facts_dict[fact_index] = Fact(text=text)
        self._facts_retriever.add_text_and_index(
            clean_text_for_retrieval(text), fact_index
        )

    def ask_for_facts(self, query):
        indices_and_scores = self._facts_retriever.get_indices_and_scores_from_text(
            query.text
        )
        threshold = (
            self._threshold_for_questions
            if query.is_question
            else self._threshold_for_facts
        )
        return [
            self._facts_dict[item[0]]
            for item in indices_and_scores
            if item[1] > threshold
        ]

    def ask_for_rule_backward(self, query):
        indices_and_scores = (
            self._rules_fact_retriever.get_indices_and_scores_from_text(query.text)
        )
        fact_rules = [
            (self._rules_dict[item[0]], item[1])
            for item in indices_and_scores
            if item[1] > self._threshold_for_facts
        ]

        indices_and_scores = (
            self._rules_question_retriever.get_indices_and_scores_from_text(query.text)
        )

        question_rules = [
            (self._rules_dict[item[0]], item[1])
            for item in indices_and_scores
            if item[1] > self._threshold_for_questions_in_rules
        ]

        indices_and_scores = (
            self._rules_incomplete_retriever.get_indices_and_scores_from_text(
                query.text
            )
        )
        incomplete_rules = [
            (self._rules_dict[item[0]], item[1])
            for item in indices_and_scores
            if item[1] > self._threshold_for_partial_facts
        ]

        return [
            item[0]
            for item in sorted(
                fact_rules + question_rules + incomplete_rules, key=lambda x: -x[1]
            )
        ]

    def _initialize_retrievers(self):
        for index, fact in self._facts_dict.items():
            self._facts_retriever.add_text_and_index(
                clean_text_for_retrieval(fact.text), index
            )

        for index, rule in self._rules_dict.items():
            if "{" in rule.effect.text:
                self._rules_incomplete_retriever.add_text_and_index(
                    clean_text_for_retrieval(rule.effect.text), index
                )
                continue

            elif rule.effect.is_question:
                self._rules_question_retriever.add_text_and_index(
                    clean_text_for_retrieval(rule.effect.text), index
                )

            else:
                self._rules_fact_retriever.add_text_and_index(
                    clean_text_for_retrieval(rule.effect.text), index
                )
