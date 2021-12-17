from unittest import TestCase

from wafl.retriever import Retriever


class TestRetrieval(TestCase):

    def test_retrieval(self):
        retriever = Retriever()
        sentences = ['this is a test', 'the food is hot on the table']
        for index, sentence in enumerate(sentences):
            retriever.add_text_and_index(sentence, str(index))

        query = 'the food is warm'
        expected = '1'
        predicted = retriever.get_indices_and_scores_from_text(query)
        assert predicted[0][0] == expected
