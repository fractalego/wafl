class BaseKnowledge:
    def add(self, text):
        raise NotImplementedError()

    def ask_for_facts(self, query, is_from_user=False):
        raise NotImplementedError()

    def ask_for_facts_with_threshold(self, query, is_from_user=False):
        raise NotImplementedError()

    def ask_for_rule_backward(self, query):
        raise NotImplementedError()
