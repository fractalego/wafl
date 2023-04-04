from wafl.answerer.base_answerer import BaseAnswerer
from wafl.extractors.dataclasses import Query
from wafl.extractors.extractor import Extractor
from wafl.inference.utils import cluster_facts


class FactAnswerer(BaseAnswerer):
    def __init__(self, knowledge, narrator, logger):
        self._knowledge = knowledge
        self._logger = logger
        self._narrator = narrator
        self._extractor = Extractor(narrator, logger)

    async def answer(self, query_text, policy):
        if self._logger:
            self._logger.write(f"Fact Answerer: the query is {query_text}")

        query = Query.create_from_text(query_text)
        facts_and_thresholds = self._knowledge.ask_for_facts_with_threshold(
            query, is_from_user=True, knowledge_name="/"
        )
        texts = cluster_facts(facts_and_thresholds)
        for text in texts:
            if self._logger:
                self._logger.write(f"Answer within facts: The query is {query_text}")
                self._logger.write(f"Answer within facts: The context is {text}")

            text = self._narrator.get_context_for_facts(text)
            answer = await self._extractor.extract(query, text)
            if self._logger:
                self._logger.write(f"Answer within facts: The answer is {answer.text}")

            if await policy.accept(answer.text):
                return answer

        text = self._narrator.summarize_dialogue()
        if self._logger:
            self._logger.write(
                f"SimpleAnswerer: The context is {text}", self._logger.level.INFO
            )
            self._logger.write(
                f"SimpleAnswerer: The query is {query_text}", self._logger.level.INFO
            )

        return await self._extractor.extract(Query(query_text, is_question=True), text)
