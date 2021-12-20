import logging

from wafl.parser import get_facts_and_rules_from_text
from wafl.retriever import Retriever
from wafl.text_utils import clean_text_for_retrieval

_logger = logging.getLogger(__name__)


class Knowledge:
    _threshold_for_questions = 0.5
    _threshold_for_facts = 0.58

    def __init__(self, rules_text):
        facts_and_rules = get_facts_and_rules_from_text(rules_text)
        self._facts_dict = {f'F{index}': value for index, value in enumerate(facts_and_rules['facts'])}
        self._rules_fact_dict = {f'RF{index}': value for index, value in enumerate(facts_and_rules['rules'])}
        self._rules_question_dict = {f'RQ{index}': value for index, value in enumerate(facts_and_rules['rules'])}
        self._facts_retriever = Retriever()
        self._rules_fact_retriever = Retriever()
        self._rules_question_retriever = Retriever()
        self._initialize_retrievers()

    def add(self, text):
        self._facts_dict[f'F{len(self._facts_dict)}'] = text

    def ask_for_facts(self, query):
        indices_and_scores = self._facts_retriever.get_indices_and_scores_from_text(query.text)
        threshold = self._threshold_for_questions if query.is_question else self._threshold_for_facts
        return [self._facts_dict[item[0]] for item in indices_and_scores if item[1] > threshold]

    def ask_for_rule_backward(self, query):
        indices_and_scores = self._rules_fact_retriever.get_indices_and_scores_from_text(query.text)
        fact_rules = [self._rules_fact_dict[item[0]] for item in indices_and_scores
                      if item[1] > self._threshold_for_facts]

        indices_and_scores = self._rules_question_retriever.get_indices_and_scores_from_text(query.text)
        question_rules = [self._rules_question_dict[item[0]] for item in indices_and_scores
                          if item[1] > self._threshold_for_questions]

        return fact_rules + question_rules

    def _initialize_retrievers(self):
        for index, fact in self._facts_dict.items():
            self._facts_retriever.add_text_and_index(clean_text_for_retrieval(fact.text),
                                                     index)

        for index, rule in self._rules_fact_dict.items():
            if rule.effect.is_question:
                continue
            self._rules_fact_retriever.add_text_and_index(clean_text_for_retrieval(rule.effect.text),
                                                          index)

        for index, rule in self._rules_question_dict.items():
            if not rule.effect.is_question:
                continue
            self._rules_question_retriever.add_text_and_index(clean_text_for_retrieval(rule.effect.text),
                                                              index)
