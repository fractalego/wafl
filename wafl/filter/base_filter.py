class BaseAnswerFilter:
    async def filter(self, dialogue_list, query_text) -> str:
        raise NotImplementedError()
