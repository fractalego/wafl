class BaseAnswerer:
    async def answer(self, query_text: str) -> "Answer":
        raise NotImplementedError
