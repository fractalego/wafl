class BaseAnswerer:
    async def answer(self, query_text):
        raise NotImplementedError
