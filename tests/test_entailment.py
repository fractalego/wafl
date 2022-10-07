import os
from unittest import TestCase

from wafl.qa.entailer import Entailer

_path = os.path.dirname(__file__)


class TestEntailment(TestCase):
    def test_fact_entailment(self):
        premise = "The user says 'hello.'."
        hypothesis = "The user is greeting"

        entailer = Entailer()
        prediction = entailer.get_relation(premise, hypothesis)
        self.assertTrue(prediction["entailment"] > 0.95)

    def test_question_entailment(self):
        premise = "The user says 'What time is the train leaving.'"
        hypothesis = "The user inquires about transport time tables"

        entailer = Entailer()
        prediction = entailer.get_relation(premise, hypothesis)
        self.assertTrue(prediction["entailment"] > 0.95)

    def test_entailment_method(self):
        premise = "The user says 'my name is John.'."
        hypothesis = "The user says their name"

        entailer = Entailer()
        self.assertEqual(entailer.entails(premise, hypothesis), "true")
