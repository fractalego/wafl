import asyncio

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.retriever.string_retriever import StringRetriever
from wafl.retriever.dense_retriever import DenseRetriever

_logger = LocalFileLogger()
_wafl_remember_rules = """
the user is tall

the user has brown hair

the user has green eyes


the user wants the bot to remember something
  sentence = What piece of information do you want me to remember?
  REMEMBER sentence
  SAY I will remember that {sentence}


"how is the user like"
  user_qualities = RETRIEVE how is the user like
  SAY {user_qualities}

"""


class TestRetrieval(TestCase):
    def test_retrieval(self):
        retriever = DenseRetriever("msmarco-distilbert-base-v3")
        sentences = ["this is a test", "the food is hot on the table"]
        for index, sentence in enumerate(sentences):
            asyncio.run(retriever.add_text_and_index(sentence, str(index)))

        query = "the food is warm"
        expected = "1"
        predicted = asyncio.run(retriever.get_indices_and_scores_from_text(query))
        assert predicted[0][0] == expected

    def test_retrieval_from_rules(self):
        interface = DummyInterface(to_utter=["tell me how the user is like"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_remember_rules, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        assert len(interface.get_utterances_list()) == 4

    def test_exact_string_retrieval(self):
        retriever = StringRetriever()
        sentences = [
            "this is a test",
            "the food is hot on the table",
            "_this is an exact string",
        ]
        for index, sentence in enumerate(sentences):
            asyncio.run(retriever.add_text_and_index(sentence, str(index)))

        query = "_this is an exact string"
        expected = "2"
        predicted = asyncio.run(retriever.get_indices_and_scores_from_text(query))
        assert predicted[0][0] == expected

    def test_short_text_retrieves_nothing(self):
        retriever = DenseRetriever("msmarco-distilbert-base-v3")
        sentences = ["The user greets"]
        for index, sentence in enumerate(sentences):
            asyncio.run(retriever.add_text_and_index(sentence, str(index)))

        query = "O uh"
        expected = []
        predicted = asyncio.run(retriever.get_indices_and_scores_from_text(query))
        assert predicted == expected

    def test_input_during_inference(self):
        interface = DummyInterface(to_utter=["Please remember that my name is Alberto"])
        conversation_events = ConversationEvents(
            SingleFileKnowledge(_wafl_remember_rules, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: I will remember that that your name is alberto"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected
