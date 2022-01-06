import logging

from wafl.conversation.utils import is_question
from wafl.facts import Fact
from wafl.inference.utils import normalized
from wafl.knowledge.base_knowledge import BaseKnowledge
from wafl.knowledge.utils import text_is_exact_string
from wafl.parsing.rules_parser import get_facts_and_rules_from_text
from wafl.retriever.string_retriever import StringRetriever
from wafl.retriever.text_retriever import TextRetriever, get_dot_product
from wafl.text_utils import clean_text_for_retrieval

_logger = logging.getLogger(__name__)


class Knowledge(BaseKnowledge):
    _threshold_for_questions = 0.51
    _threshold_for_questions_in_rules = 0.49
    _threshold_for_facts = 0.58
    _threshold_for_partial_facts = 0.42
    _interruption_question_penalty = 0.2
    _interruption_answer_penalty = 0.4
    _interruption_story_penalty = 0.4

    def __init__(self, rules_text=None):
        facts_and_rules = get_facts_and_rules_from_text(rules_text)
        self._facts_dict = {
            f"F{index}": value for index, value in enumerate(facts_and_rules["facts"])
        }
        self._rules_dict = {
            f"R{index}": value for index, value in enumerate(facts_and_rules["rules"])
        }
        self._facts_retriever = TextRetriever()
        self._rules_incomplete_retriever = TextRetriever()
        self._rules_fact_retriever = TextRetriever()
        self._rules_question_retriever = TextRetriever()
        self._rules_string_retriever = StringRetriever()
        self._initialize_retrievers()

    def add(self, text):
        fact_index = f"F{len(self._facts_dict)}"
        self._facts_dict[fact_index] = Fact(text=text)
        self._facts_retriever.add_text_and_index(
            clean_text_for_retrieval(text), fact_index
        )

    def has_better_match(self, question: str, answer: str, story: str) -> bool:
        if len(answer) < len("the user say"):
            return False

        if any(normalized(answer).find(item) == 0 for item in ["yes", "no"]):
            return False

        if any(normalized(answer).find(item) != -1 for item in [" yes", " no"]):
            return False

        answer_dot_product = get_dot_product(question, answer)
        story_dot_product = get_dot_product(story, answer)

        indices_and_scores = self._facts_retriever.get_indices_and_scores_from_text(
            answer
        )
        indices_and_scores += (
            self._rules_fact_retriever.get_indices_and_scores_from_text(answer)
        )
        indices_and_scores += (
            self._rules_question_retriever.get_indices_and_scores_from_text(answer)
        )
        indices_and_scores += (
            self._rules_incomplete_retriever.get_indices_and_scores_from_text(answer)
        )

        if not is_question(answer):
            return any(
                item[1] - self._interruption_answer_penalty > answer_dot_product
                and item[1] - self._interruption_story_penalty > story_dot_product
                for item in indices_and_scores
            )

        return any(
            item[1] - self._interruption_question_penalty > answer_dot_product
            for item in indices_and_scores
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

        return [
            item[0]
            for item in sorted(
                fact_rules + question_rules + incomplete_rules, key=lambda x: -x[1]
            )
        ]

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
