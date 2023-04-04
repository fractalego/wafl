class BaseAnswerer:
    async def answer(self, query_text, policy):
        raise NotImplementedError
