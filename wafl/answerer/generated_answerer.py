from wafl.answerer.base_answerer import BaseAnswerer
from wafl.connectors.gptj_generated_answer_connector import GPTJGeneratedAnswerConnector


class GeneratedAnswerer(BaseAnswerer):
    def __init__(self, narrator, logger):
        self._logger = logger
        self._narrator = narrator
        self._connector = GPTJGeneratedAnswerConnector()

    async def answer(self, query_text):
        self._logger.write(f"Generated Answerer: the query is {query_text}")
        answer_text = self._connector.get_answer(
            text="", dialogue=None, query=query_text
        )
        self._logger.write(f"Generated Answerer: the answer is {answer_text}")
        return answer_text
