from unittest import TestCase

from wafl.inference import BackwardInference
from wafl.knowledge import Knowledge
from wafl.qa.qa import Query

wafl_example = """

The user greets
  What is the user's name ? username
  SAY hello to you, {username}!

The user says they can swim
  What is the user's name ? username
  USER is called {username}
  
What is the user's hair color ? color
  What is the user's name ? username
  {username} has {color} hair

This bot name is Fractalego

the user is very happy

The user's name is Bob

Bob has black hair

""".strip()


class TestInference(TestCase):

    def test_simple_question(self):
        inference = BackwardInference(Knowledge(wafl_example))
        query = Query(text="What is this bot's name", is_question=True, variable='name')
        answer = inference.compute(query)
        expected = "Fractalego"
        assert answer.text == expected
        assert answer.variable == query.variable

    def test_fact_check_true(self):
        inference = BackwardInference(Knowledge(wafl_example))
        query = Query(text="The user is in a good mood", is_question=False, variable='name')
        answer = inference.compute(query)
        expected = "True"
        assert answer.text == expected

    def test_fact_check_false(self):
        inference = BackwardInference(Knowledge(wafl_example))
        query = Query(text="The user is sad", is_question=False, variable='name')
        answer = inference.compute(query)
        expected = "False"
        assert answer.text == expected

    def test_simple_rule(self):
        inference = BackwardInference(Knowledge(wafl_example))
        query = Query(text="The user says hello!", is_question=False, variable='name')
        answer = inference.compute(query)
        expected = "True"
        assert answer.text == expected

    def test_forward_substitution(self):
        inference = BackwardInference(Knowledge(wafl_example))
        query = Query(text="The user says: I can swim", is_question=False, variable='name')
        answer = inference.compute(query)
        expected = "True"
        assert answer.text == expected

    def test_backward_substitution(self):
        inference = BackwardInference(Knowledge(wafl_example))
        query = Query(text="The user says: I have black hair", is_question=False, variable='name')
        answer = inference.compute(query)
        expected = "True"
        assert answer.text == expected
