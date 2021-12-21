class BaseKnowledge:
    def add(self, text):
        raise NotImplemented()

    def ask_for_facts(self, query):
        raise NotImplemented()

    def ask_for_rule_backward(self, query):
        raise NotImplemented()
