from unittest import TestCase

from wafl.conversation.utils import is_question


class TestQuestions(TestCase):
    def test_are_question(self):
        utterance = "Are you interested in this platter of fish"
        assert is_question(utterance)

    def test_am_question(self):
        utterance = "Am I interested in this platter of fish"
        assert is_question(utterance)

    def test_am_question(self):
        utterance = "Am I interested in this platter of fish"
        assert is_question(utterance)
