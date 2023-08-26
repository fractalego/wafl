class BaseKnowledge:
    root_knowledge = "/"

    async def add(self, text):
        raise NotImplementedError()

    async def add_rule(self, rule_text, knowledge_name=None):
        raise NotImplementedError()

    async def ask_for_facts(self, query, is_from_user=False, knowledge_name=None):
        raise NotImplementedError()

    async def ask_for_facts_with_threshold(
        self, query, is_from_user=False, knowledge_name=None, threshold=None
    ):
        raise NotImplementedError()

    async def ask_for_rule_backward(self, query, knowledge_name=None, first_n=None):
        raise NotImplementedError()

    async def has_better_match(self, query_text: str) -> bool:
        raise NotImplementedError()
