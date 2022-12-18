from unittest import TestCase

from wafl.retriever.string_retriever import StringRetriever
from wafl.retriever.dense_retriever import DenseRetriever

_wafl_greetings = """

The user says their name
  SAY Hello there!
  username = What is the user's name
  SAY Nice to meet you, {username}!

""".strip()


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
