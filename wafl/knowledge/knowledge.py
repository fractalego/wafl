import logging
import nltk

from wafl.facts import Fact
from wafl.inference.utils import normalized
from wafl.knowledge.base_knowledge import BaseKnowledge
from wafl.knowledge.utils import (
    text_is_exact_string,
    rules_are_too_different,
    get_first_cluster_of_rules,
    filter_out_rules_that_are_too_dissimilar_to_query,
    filter_out_rules_through_entailment,
)
from wafl.parsing.rules_parser import get_facts_and_rules_from_text
from wafl.qa.entailer import Entailer
from wafl.qa.dataclasses import Query
from wafl.retriever.string_retriever import StringRetriever
from wafl.retriever.dense_retriever import DenseRetriever
from wafl.text_utils import clean_text_for_retrieval

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

_logger = logging.getLogger(__name__)


class Knowledge(BaseKnowledge):
    _threshold_for_questions_from_user = 0.6
    _threshold_for_questions_from_bot = 0.6
    _threshold_for_questions_in_rules = 0.505
    _threshold_for_facts = 0.4
    _threshold_for_partial_facts = 0.48

    def __init__(self, rules_text=None, logger=None):
        facts_and_rules = get_facts_and_rules_from_text(rules_text)
        self._facts_dict = {
            f"F{index}": value for index, value in enumerate(facts_and_rules["facts"])
        }
        self._rules_dict = {
            f"R{index}": value for index, value in enumerate(facts_and_rules["rules"])
        }
        self._facts_retriever = DenseRetriever("msmarco-distilbert-base-v3")
        self._facts_retriever_for_questions = DenseRetriever(
            "multi-qa-distilbert-dot-v1"
        )
        self._logger = logger
        self._entailer = Entailer(logger)
        self._rules_incomplete_retriever = DenseRetriever("msmarco-distilbert-base-v3")
        self._rules_fact_retriever = DenseRetriever("msmarco-distilbert-base-v3")
        self._rules_question_retriever = DenseRetriever("msmarco-distilbert-base-v3")
        self._rules_string_retriever = StringRetriever()
        self._initialize_retrievers()

    def add(self, text):
        fact_index = f"F{len(self._facts_dict)}"
        self._facts_dict[fact_index] = Fact(text=text)
        self._facts_retriever.add_text_and_index(
            clean_text_for_retrieval(text), fact_index
        )
        self._facts_retriever_for_questions.add_text_and_index(
            clean_text_for_retrieval(text), fact_index
        )

    def has_better_match(self, answer: str) -> bool:
        if any(normalized(answer).find(item) == 0 for item in ["yes", "no"]):
            return False

        if any(normalized(answer).find(item) != -1 for item in [" yes ", " no "]):
            return False

        rules = self.ask_for_rule_backward(
            Query(text=f"The user says to the bot: '{answer}.'", is_question=False)
        )
        return any(rule.effect.is_interruption for rule in rules)

    def ask_for_facts(self, query, is_from_user=False):
        if query.is_question:
            indices_and_scores = (
                self._facts_retriever_for_questions.get_indices_and_scores_from_text(
                    query.text
                )
            )

        else:
            indices_and_scores = self._facts_retriever.get_indices_and_scores_from_text(
                query.text
            )
        if is_from_user:
            threshold = (
                self._threshold_for_questions_from_user
                if query.is_question
                else self._threshold_for_facts
            )
        else:
            threshold = (
                self._threshold_for_questions_from_bot
                if query.is_question
                else self._threshold_for_facts
            )

        return [
            self._facts_dict[item[0]]
            for item in indices_and_scores
            if item[1] > threshold
        ]

    def ask_for_facts_with_threshold(self, query, is_from_user=False):
        if query.is_question:
            indices_and_scores = (
                self._facts_retriever_for_questions.get_indices_and_scores_from_text(
                    query.text
                )
            )

        else:
            indices_and_scores = self._facts_retriever.get_indices_and_scores_from_text(
                query.text
            )
        if is_from_user:
            threshold = (
                self._threshold_for_questions_from_user
                if query.is_question
                else self._threshold_for_facts
            )
        else:
            threshold = (
                self._threshold_for_questions_from_bot
                if query.is_question
                else self._threshold_for_facts
            )

        return [
            (self._facts_dict[item[0]], item[1])
            for item in indices_and_scores
            if item[1] > threshold
        ]

    def ask_for_rule_backward(self, query):
        if text_is_exact_string(query.text):
            indices_and_scores = (
                self._rules_string_retriever.get_indices_and_scores_from_text(
                    query.text
                )
            )
            return [self._rules_dict[item[0]] for item in indices_and_scores]

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

        rules_and_scores = [
            item
            for item in sorted(
                fact_rules + question_rules + incomplete_rules, key=lambda x: -x[1]
            )
        ]

        rules = [item[0] for item in rules_and_scores]
        if rules_are_too_different(self._rules_fact_retriever, rules):
            return []

        rules_and_scores = filter_out_rules_that_are_too_dissimilar_to_query(
            query, rules_and_scores
        )

        rules_and_scores = filter_out_rules_through_entailment(
            self._entailer, query, rules_and_scores
        )

        return get_first_cluster_of_rules(rules_and_scores)

    def get_facts_and_rule_as_text(self):
        text = ""
        for fact in self._facts_dict.values():
            text += fact.text + "\n"

        for effect in self._rules_dict.values():
            text += effect.effect.text + "\n"

        return text

    def _initialize_retrievers(self):
        for index, fact in self._facts_dict.items():
            if text_is_exact_string(fact.text):
                continue

            self._facts_retriever.add_text_and_index(
                clean_text_for_retrieval(fact.text), index
            )

            self._facts_retriever_for_questions.add_text_and_index(
                clean_text_for_retrieval(fact.text), index
            )

        for index, rule in self._rules_dict.items():
            if text_is_exact_string(rule.effect.text):
                continue

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

        for index, rule in self._rules_dict.items():
            if not text_is_exact_string(rule.effect.text):
                continue

            self._rules_string_retriever.add_text_and_index(rule.effect.text, index)
