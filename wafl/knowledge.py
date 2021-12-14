import logging

from wafl.parser import get_facts_and_rules_from_text

_logger = logging.getLogger(__name__)


class Knowledge:
    def __init__(self, rules_text):
        facts_and_rules = get_facts_and_rules_from_text(rules_text)
        self._facts = facts_and_rules['facts']
        self._rules = facts_and_rules['rules']

    def ask_drs(self, drs):
        pass

    def ask_rule(self, drs):
        return self._rules

    def ask_rule_fw(self, drs):
        return self._rules

    def ask_rule_bw(self, drs):
        return self._rules
