class BaseKnowledge:
    def add(self, text):
        raise NotImplemented()

    def ask_for_facts(self, query, is_from_user=False):
        raise NotImplemented()

    def ask_for_rule_backward(self, query):
        raise NotImplemented()
