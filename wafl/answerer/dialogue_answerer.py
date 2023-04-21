import time

from wafl.answerer.base_answerer import BaseAnswerer
from wafl.connectors.gptj_chitchat_answer_connector import GPTJChitChatAnswerConnector
from wafl.extractors.dataclasses import Query, Answer
from wafl.inference.utils import cluster_facts


class DialogueAnswerer(BaseAnswerer):
    def __init__(self, knowledge, interface, logger):
        self._knowledge = knowledge
        self._logger = logger
        self._interface = interface
        self._connector = GPTJChitChatAnswerConnector()
        self._max_num_past_utterances = 7

    async def answer(self, query_text, policy):
        if self._logger:
            self._logger.write(f"Dialogue Answerer: the query is {query_text}")

        query = Query.create_from_text(query_text)
        facts_and_thresholds = self._knowledge.ask_for_facts_with_threshold(
            query, is_from_user=True, knowledge_name="/"
        )
        texts = cluster_facts(facts_and_thresholds)
        for text in texts:
            self._interface.add_fact(f"The bot remembers: {text}")

        dialogue = self._interface.get_utterances_list_with_timestamp()[
            -self._max_num_past_utterances :
        ]
        start_time = -1
        if dialogue:
            start_time = dialogue[0][0]

        if not dialogue:
            dialogue = [(time.time(), f"user: {query_text}")]

        choices = self._interface.get_choices_and_timestamp()
        facts = self._interface.get_facts_and_timestamp()
        dialogue_items = dialogue + choices + facts
        dialogue_items = sorted(dialogue_items, key=lambda x: x[0])
        dialogue_items = [item[1] for item in dialogue_items if item[0] >= start_time]
        dialogue_items = "\n".join(dialogue_items)
        answer_text = await self._connector.get_answer(
            text="",
            dialogue=dialogue_items,
            query=query_text,
        )
        if self._logger:
            self._logger.write(f"Answer within dialogue: The answer is {answer_text}")

        if await policy.accept(answer_text):
            return Answer.create_from_text(answer_text)

        return Answer.create_neutral()
