import asyncio
import logging
from typing import List

import nltk

from wafl.config import Configuration
from wafl.facts import Fact
from wafl.knowledge.base_knowledge import BaseKnowledge
from wafl.knowledge.utils import (
    text_is_exact_string,
    get_first_cluster_of_rules,
)
from wafl.parsing.line_rules_parser import parse_rule_from_single_line
from wafl.parsing.rules_parser import get_facts_and_rules_from_text
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
    _threshold_for_facts = 0.7
    _threshold_for_rules = 0.85
    _max_rules_per_type = 3

    def __init__(self, config, rules_text=None, logger=None):
        self._logger = logger
        self._facts_dict = {}
        self._rules_dict = {}
        self._facts_retriever = DenseRetriever("text_embedding_model", config)
        self._facts_retriever_for_questions = DenseRetriever(
            "text_embedding_model",
            config,
        )
        self._rules_retriever = DenseRetriever("text_embedding_model", config)
        self._rules_string_retriever = StringRetriever()
        if rules_text:
            facts_and_rules = get_facts_and_rules_from_text(rules_text)
            self._facts_dict = {
                f"F{index}": value
                for index, value in enumerate(facts_and_rules["facts"])
            }
            self._rules_dict = {
                f"R{index}": value
                for index, value in enumerate(facts_and_rules["rules"])
            }
            try:
                loop = asyncio.get_running_loop()

            except RuntimeError:
                loop = None

            if not loop or not loop.is_running():
                asyncio.run(self._initialize_retrievers())

    async def add(self, text):
        fact_index = f"F{len(self._facts_dict)}"
        self._facts_dict[fact_index] = Fact(text=text)
        await self._facts_retriever.add_text_and_index(
            clean_text_for_retrieval(text), fact_index
        )
        await self._facts_retriever_for_questions.add_text_and_index(
            clean_text_for_retrieval(text), fact_index
        )

    async def add_rule(self, rule_text):
        rule = parse_rule_from_single_line(rule_text)
        index = str(len(self._rules_dict))
        index = f"R{index}"
        self._rules_dict[index] = rule
        await self._rules_retriever.add_text_and_index(
            clean_text_for_retrieval(rule.effect.text), index=index
        )

    async def ask_for_facts(self, query, is_from_user=False, threshold=None):
        if query.is_question:
            indices_and_scores = await self._facts_retriever_for_questions.get_indices_and_scores_from_text(
                query.text
            )

        else:
            indices_and_scores = (
                await self._facts_retriever.get_indices_and_scores_from_text(query.text)
            )
        if threshold == None and is_from_user:
            threshold = (
                self._threshold_for_questions_from_user
                if query.is_question
                else self._threshold_for_facts
            )
        elif threshold == None:
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

    async def ask_for_facts_with_threshold(
        self, query, is_from_user=False, threshold=None
    ):
        if query.is_question:
            indices_and_scores = await self._facts_retriever_for_questions.get_indices_and_scores_from_text(
                query.text
            )

        else:
            indices_and_scores = (
                await self._facts_retriever.get_indices_and_scores_from_text(query.text)
            )

        if threshold == None and is_from_user:
            threshold = (
                self._threshold_for_questions_from_user
                if query.is_question
                else self._threshold_for_facts
            )

        elif threshold == None:
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

    async def ask_for_rule_backward(self, query, threshold=None):
        rules_and_scores = await self._ask_for_rule_backward_with_scores(
            query, threshold=threshold
        )
        return get_first_cluster_of_rules(rules_and_scores)

    def get_facts_and_rule_as_text(self):
        text = ""
        for fact in self._facts_dict.values():
            text += fact.text + "\n"

        for effect in self._rules_dict.values():
            text += effect.effect.text + "\n"

        return text

    async def _initialize_retrievers(self):
        for index, fact in self._facts_dict.items():
            if text_is_exact_string(fact.text):
                continue

            await self._facts_retriever.add_text_and_index(
                clean_text_for_retrieval(fact.text), index
            )

            await self._facts_retriever_for_questions.add_text_and_index(
                clean_text_for_retrieval(fact.text), index
            )

        for index, rule in self._rules_dict.items():
            if text_is_exact_string(rule.effect.text):
                continue

            await self._rules_retriever.add_text_and_index(
                clean_text_for_retrieval(rule.effect.text), index
            )

        for index, rule in self._rules_dict.items():
            if not text_is_exact_string(rule.effect.text):
                continue

            await self._rules_string_retriever.add_text_and_index(
                rule.effect.text, index
            )

    @staticmethod
    async def create_from_list(
        facts: List[str], config: "Configuration" = None
    ) -> "SingleFileKnowledge":
        if not config:
            config = Configuration.load_local_config()

        knowledge = SingleFileKnowledge(config)
        for index, fact in enumerate(facts):
            await knowledge.add(fact)

        return knowledge

    async def _ask_for_rule_backward_with_scores(self, query, threshold=None):
        if text_is_exact_string(query.text):
            indices_and_scores = (
                await self._rules_string_retriever.get_indices_and_scores_from_text(
                    query.text
                )
            )
            return [(self._rules_dict[item[0]], item[1]) for item in indices_and_scores]

        indices_and_scores = (
            await self._rules_retriever.get_indices_and_scores_from_text(query.text)
        )

        if threshold == None:
            threshold = self._threshold_for_rules

        rules = [
            (self._rules_dict[item[0]], item[1])
            for item in indices_and_scores
            if item[1] > threshold
        ]

        rules = [item for item in sorted(rules, key=lambda x: -x[1])][
            : self._max_rules_per_type
        ]

        rules_and_scores = rules
        return rules_and_scores
