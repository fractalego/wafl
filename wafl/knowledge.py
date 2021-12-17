import logging

from wafl.parser import get_facts_and_rules_from_text
from wafl.retriever import Retriever
from wafl.text_utils import clean_text_for_retrieval

_logger = logging.getLogger(__name__)


class Knowledge:
    _threshold = 0.5

    def __init__(self, rules_text):
        facts_and_rules = get_facts_and_rules_from_text(rules_text)
        self._facts_dict = {f'F{index}': value for index, value in enumerate(facts_and_rules['facts'])}
        self._rules_dict = {f'R{index}': value for index, value in enumerate(facts_and_rules['rules'])}
        self._facts_retriever = Retriever()
        self._rules_retriever = Retriever()
        self._initialize_retrievers()

    def add(self, text):
        self._facts_dict[f'F{len(self._facts_dict)}'] = text

    def ask_for_facts(self, text):
        indices_and_scores = self._facts_retriever.get_indices_and_scores_from_text(text)
        return [self._facts_dict[item[0]] for item in indices_and_scores if item[1] > self._threshold]

    def ask_for_rule_backward(self, text):
        indices_and_scores = self._rules_retriever.get_indices_and_scores_from_text(text)
        return [self._rules_dict[item[0]] for item in indices_and_scores if item[1] > self._threshold]

    def _initialize_retrievers(self):
        for index, fact in self._facts_dict.items():
            self._facts_retriever.add_text_and_index(clean_text_for_retrieval(fact.text),
                                                     index)

        for index, rule in self._rules_dict.items():
            self._rules_retriever.add_text_and_index(clean_text_for_retrieval(rule.effect),
                                                     index)
