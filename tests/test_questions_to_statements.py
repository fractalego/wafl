import asyncio
import os

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.narrator import Narrator
from wafl.simple_text_processing.questions import get_sentence_from_yn_question
from wafl.interface.dummy_interface import DummyInterface
from wafl.extractors.dataclasses import Query
from wafl.extractors.extractor import Extractor

_path = os.path.dirname(__file__)


class TestQuestionsToStatements(TestCase):
    def test__yn_question_is_translated_to_sentence1(self):
        text = "is this bot doing well?"
        prediction = get_sentence_from_yn_question(text)
        expected = "this bot is doing well"
        self.assertEqual(expected, prediction)

    def test__yn_question_is_translated_to_sentence2(self):
        text = "are all the systems nominal?"
        prediction = get_sentence_from_yn_question(text)
        expected = "all the systems are nominal"
        self.assertEqual(expected, prediction)

    def test__yn_question_is_translated_to_sentence3(self):
        text = "Did Bob sell the house?"
        prediction = get_sentence_from_yn_question(text)
        expected = "Bob did sell the house"
        self.assertEqual(expected, prediction)

    def test__yn_question_is_translated_to_sentence4(self):
        text = "Did he sell the house?"
        prediction = get_sentence_from_yn_question(text)
        expected = "he did sell the house"
        self.assertEqual(expected, prediction)

    def test__yn_questions_use_entailer_for_positive_answers(self):
        text = "This bot is doing well"
        query = Query("is this bot ok?", is_question=True)
        config = Configuration.load_local_config()
        qa = Extractor(config, Narrator(DummyInterface))
        prediction = asyncio.run(qa.extract(query, text))
        self.assertEqual("yes", prediction.text.lower())
