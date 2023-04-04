from wafl.answerer.base_answerer import BaseAnswerer
from wafl.extractors.dataclasses import Query, Answer
from wafl.extractors.extractor import Extractor
from wafl.simple_text_processing.questions import is_question


class SimpleAnswerer(BaseAnswerer):
    def __init__(self, narrator, logger):
        self._extractor = Extractor(narrator, logger)
        self._logger = logger
        self._narrator = narrator

    async def answer(self, query_text, policy):
        if not is_question(query_text):
            return Answer(text="unknown")

        text = self._narrator.summarize_dialogue()
        if self._logger:
            self._logger.write(
                f"SimpleAnswerer: The context is {text}", self._logger.level.INFO
            )
            self._logger.write(
                f"SimpleAnswerer: The query is {query_text}", self._logger.level.INFO
            )

        answer = await self._extractor.extract(
            Query(query_text, is_question=True), text
        )
        if await policy.accept(answer.text):
            return answer

        return Answer.create_neutral()
