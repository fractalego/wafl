from wafl.qa.dataclasses import Query
from wafl.qa.qa import QA


class Answerer:
    def __init__(self, logger):
        self._qa = QA(logger)
        self._logger = logger

    def answer(self, text, query_text):
        if self._logger:
            self._logger.write(
                f"Answerer: The context is {text}", self._logger.level.INFO
            )
            self._logger.write(
                f"Answerer: The query is {query_text}", self._logger.level.INFO
            )

        return self._qa.ask(Query(query_text, is_question=True), text)
