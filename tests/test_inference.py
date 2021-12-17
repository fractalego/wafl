from unittest import TestCase

from wafl.inference import BackwardInference
from wafl.knowledge import Knowledge
from wafl.qa.qa import Query

wafl_example = """

USER greets
  What is the user's name ? username
  SAY hello to you, {username}!

USER says their name
  USER is called {username}
  SAY nice to meet you {username}

This bot name is Fractalego

the user is very happy

The user's name is Bob

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

#    def test_conversation(self):
#        conversation = Conversation(Knowledge(wafl_example))
#        conversation.utter('Welcome to the website. How may I help you?')
#
#        while conversation.ongoing():
#            utterance = conversation.next()
#            print(utterance)
#
#            if utterance.is_question:
#                answer = input()
#                conversation.answer(answer)
