from wafl.answerer.base_answerer import BaseAnswerer
from wafl.extractor.dataclasses import Query
from wafl.extractor.extractor import Extractor


class SimpleAnswerer(BaseAnswerer):
    def __init__(self, narrator, logger):
        self._extractor = Extractor(narrator, logger)
        self._logger = logger
        self._narrator = narrator

    async def answer(self, query_text):
        text = self._narrator.summarize_dialogue()
        if self._logger:
            self._logger.write(
                f"SimpleAnswerer: The context is {text}", self._logger.level.INFO
            )
            self._logger.write(
                f"SimpleAnswerer: The query is {query_text}", self._logger.level.INFO
            )

        return self._extractor.extract(Query(query_text, is_question=True), text)
