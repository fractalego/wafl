class BaseKnowledge:
    root_knowledge = "/"

    async def add(self, text):
        raise NotImplementedError()

    async def add_rule(self, rule_text):
        raise NotImplementedError()

    async def ask_for_facts(self, query, is_from_user=False):
        raise NotImplementedError()

    async def ask_for_facts_with_threshold(
        self, query, is_from_user=False, threshold=None
    ):
        raise NotImplementedError()

    async def ask_for_rule_backward(self, query, threshold=None):
        raise NotImplementedError()
