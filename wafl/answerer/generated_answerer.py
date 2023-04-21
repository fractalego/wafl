from wafl.answerer.base_answerer import BaseAnswerer
from wafl.connectors.gptj_generated_answer_connector import GPTJGeneratedAnswerConnector
from wafl.extractors.dataclasses import Answer
from wafl.extractors.entailer import Entailer


class GeneratedAnswerer(BaseAnswerer):
    def __init__(self, narrator, logger):
        self._logger = logger
        self._narrator = narrator
        self._connector = GPTJGeneratedAnswerConnector()
        self._entailer = Entailer(logger)

    async def answer(self, query_text, policy):
        if self._logger:
            self._logger.write(f"Generated Answerer: the query is {query_text}")

        answer_text = await self._connector.get_answer(
            text="", dialogue=None, query=query_text
        )
        if self._logger:
            self._logger.write(f"Generated Answerer: the answer is {answer_text}")

        if await self._entailer.is_neutral(
            self._narrator.summarize_dialogue(), answer_text
        ) and await policy.accept(answer_text):
            return Answer(text=answer_text)

        return Answer.create_neutral()
