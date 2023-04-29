import logging
from typing import List

import nltk

from wafl.facts import Fact
from wafl.simple_text_processing.normalize import normalized
from wafl.knowledge.base_knowledge import BaseKnowledge
from wafl.knowledge.utils import (
    text_is_exact_string,
    rules_are_too_different,
    get_first_cluster_of_rules,
    filter_out_rules_that_are_too_dissimilar_to_query,
    filter_out_rules_through_entailment,
)
from wafl.parsing.line_rules_parser import parse_rule_from_single_line
from wafl.parsing.rules_parser import get_facts_and_rules_from_text
from wafl.extractors.entailer import Entailer
from wafl.extractors.dataclasses import Query
from wafl.retriever.string_retriever import StringRetriever
from wafl.retriever.dense_retriever import DenseRetriever
from wafl.text_utils import clean_text_for_retrieval

nltk.download("punkt")
nltk.download("averaged_perceptron_tagger")

_logger = logging.getLogger(__name__)


class SingleFileKnowledge(BaseKnowledge):
    _threshold_for_questions_from_user = 0.55
    _threshold_for_questions_from_bot = 0.6
    _threshold_for_questions_in_rules = 0.49
    _threshold_for_facts = 0.4
    _threshold_for_fact_rules = 0.35
    _threshold_for_partial_facts = 0.48
    _max_rules_per_type = 3

    def __init__(self, rules_text=None, knowledge_name=None, logger=None):
        self._logger = logger
        self._facts_dict = {}
        self._rules_dict = {}
        self._facts_retriever = DenseRetriever("msmarco-distilbert-base-v3")
        self._facts_retriever_for_questions = DenseRetriever(
            "multi-qa-distilbert-dot-v1"
        )
        self._entailer = Entailer(logger)
        self._rules_incomplete_retriever = DenseRetriever("msmarco-distilbert-base-v3")
        self._rules_fact_retriever = DenseRetriever("msmarco-distilbert-base-v3")
        self._rules_question_retriever = DenseRetriever("msmarco-distilbert-base-v3")
        self._rules_string_retriever = StringRetriever()
        knowledge_name = knowledge_name if knowledge_name else self.root_knowledge
        if rules_text:
            facts_and_rules = get_facts_and_rules_from_text(
                rules_text, knowledge_name=knowledge_name
            )
            self._facts_dict = {
                f"F{index}": value
                for index, value in enumerate(facts_and_rules["facts"])
            }
            self._rules_dict = {
                f"R{index}": value
                for index, value in enumerate(facts_and_rules["rules"])
            }
            self._initialize_retrievers()

    def add(self, text, knowledge_name="/"):
        fact_index = f"F{len(self._facts_dict)}"
        self._facts_dict[fact_index] = Fact(text=text, knowledge_name=knowledge_name)
        self._facts_retriever.add_text_and_index(
            clean_text_for_retrieval(text), fact_index
        )
        self._facts_retriever_for_questions.add_text_and_index(
            clean_text_for_retrieval(text), fact_index
        )

    def add_rule(self, rule_text, knowledge_name=None):
        rule = parse_rule_from_single_line(rule_text, knowledge_name)
        index = str(len(self._rules_dict))
        index = f"R{index}"
        self._rules_dict[index] = rule
        self._rules_fact_retriever.add_text_and_index(
            clean_text_for_retrieval(rule.effect.text), index=index
        )

    async def has_better_match(self, query_text: str) -> bool:
        if any(normalized(query_text).find(item) == 0 for item in ["yes", "no"]):
            return False

        if any(normalized(query_text).find(item) != -1 for item in [" yes ", " no "]):
            return False

        rules = await self.ask_for_rule_backward(
            Query(text=f"The user says to the bot: '{query_text}.'", is_question=False)
        )
        return any(rule.effect.is_interruption for rule in rules)

    def ask_for_facts(
        self, query, is_from_user=False, knowledge_name=None, threshold=None
    ):
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
        if not threshold and is_from_user:
            threshold = (
                self._threshold_for_questions_from_user
                if query.is_question
                else self._threshold_for_facts
            )
        elif not threshold:
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

    def ask_for_facts_with_threshold(
        self, query, is_from_user=False, knowledge_name=None
    ):
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

    async def ask_for_rule_backward(self, query, knowledge_name=None):
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
            if item[1] > self._threshold_for_fact_rules
        ]
        fact_rules = [item for item in sorted(fact_rules, key=lambda x: -x[1])][
            : self._max_rules_per_type
        ]

        indices_and_scores = (
            self._rules_question_retriever.get_indices_and_scores_from_text(query.text)
        )
        question_rules = [
            (self._rules_dict[item[0]], item[1])
            for item in indices_and_scores
            if item[1] > self._threshold_for_questions_in_rules
        ]
        question_rules = [item for item in sorted(question_rules, key=lambda x: -x[1])][
            : self._max_rules_per_type
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
        incomplete_rules = [
            item for item in sorted(incomplete_rules, key=lambda x: -x[1])
        ][: self._max_rules_per_type]

        rules_and_scores = fact_rules + question_rules + incomplete_rules
        rules = [item[0] for item in rules_and_scores]
        if rules_are_too_different(self._rules_fact_retriever, rules):
            return []

        rules_and_scores = filter_out_rules_that_are_too_dissimilar_to_query(
            query, rules_and_scores
        )

        rules_and_scores = await filter_out_rules_through_entailment(
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

    @staticmethod
    def create_from_list(facts: List[str]):
        knowledge = SingleFileKnowledge()
        for index, fact in enumerate(facts):
            knowledge.add(fact)

        return knowledge
