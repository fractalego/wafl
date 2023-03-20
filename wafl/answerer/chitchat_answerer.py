from wafl.answerer.base_answerer import BaseAnswerer
from wafl.connectors.gptj_chitchat_answer_connector import GPTJChitChatAnswerConnector
from wafl.extractors.dataclasses import Answer
from wafl.simple_text_processing.questions import is_question


class ChitChatAnswerer(BaseAnswerer):
    def __init__(self, narrator, logger):
        self._logger = logger
        self._narrator = narrator
        self._connector = GPTJChitChatAnswerConnector()

    async def answer(self, query_text, policy):
        if self._logger:
            self._logger.write(f"Generated Answerer: the query is {query_text}")

        if is_question(query_text):
            if self._logger:
                self._logger.write(f"Generated Answerer: returning unknown")

            return Answer(text="unknown")

        answer_text = await self._connector.get_answer(
            text="",
            dialogue="\n".join(self._narrator._interface.get_utterances_list()),
            query=query_text,
        )
        if self._logger:
            self._logger.write(f"Generated Answerer: the answer is {answer_text}")

        if await policy.accept(answer_text):
            return Answer(text=answer_text)

        return Answer.create_neutral()
