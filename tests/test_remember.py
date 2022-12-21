from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.logger.local_file_logger import LocalFileLogger
from wafl.retriever.string_retriever import StringRetriever
from wafl.retriever.dense_retriever import DenseRetriever

_logger = LocalFileLogger()
_wafl_remember_rules = """

the user wants you to remember 
  sentence = What do you want me to remember?
  REMEMBER sentence
  SAY I will remember that {sentence}

"""


class TestRetrieval(TestCase):
    def test_retrieval(self):
        retriever = DenseRetriever("msmarco-distilbert-base-v3")
        sentences = ["this is a test", "the food is hot on the table"]
        for index, sentence in enumerate(sentences):
            retriever.add_text_and_index(sentence, str(index))

        query = "the food is warm"
        expected = "1"
        predicted = retriever.get_indices_and_scores_from_text(query)
        assert predicted[0][0] == expected

    def test_exact_string_retrieval(self):
        retriever = StringRetriever()
        sentences = [
            "this is a test",
            "the food is hot on the table",
            "_this is an exact string",
        ]
        for index, sentence in enumerate(sentences):
            retriever.add_text_and_index(sentence, str(index))

        query = "_this is an exact string"
        expected = "2"
        predicted = retriever.get_indices_and_scores_from_text(query)
        assert predicted[0][0] == expected

    def test_short_text_retrieves_nothing(self):
        retriever = DenseRetriever("msmarco-distilbert-base-v3")
        sentences = ["The user greets"]
        for index, sentence in enumerate(sentences):
            retriever.add_text_and_index(sentence, str(index))

        query = "O uh"
        expected = []
        predicted = retriever.get_indices_and_scores_from_text(query)
        assert predicted == expected

    def test_input_during_inference(self):
        interface = DummyInterface(to_utter=["Please remember that my name is Alberto"])
        conversation = Conversation(
            Knowledge(_wafl_remember_rules, logger=_logger),
            interface=interface,
            logger=_logger,
        )
        conversation.input()
        expected = "bot: I will remember that your name is alberto"
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected
