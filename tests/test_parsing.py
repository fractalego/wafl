from unittest import TestCase

from wafl.facts import Fact
from wafl.knowledge.knowledge import Knowledge
from wafl.parsing.parser import get_facts_and_rules_from_text
from wafl.qa.qa import Query
from wafl.rules import Rule

wafl_example = """

USER greets
  USER is called {username}
  SAY hello to you, {username}!

USER says their name
  USER is called {username}
  nice to meet you {username}
  
BOT name is Fractalego

the user is happy

""".strip()


class TestParsing(TestCase):
    def test_rules_parsing(self):
        facts_and_rules = get_facts_and_rules_from_text(wafl_example)
        expected = str(
            [
                Rule(
                    effect=Fact(text="USER greets", is_question=False),
                    causes=[
                        Fact(text="USER is called {username}", is_question=False),
                        Fact(text="SAY hello to you, {username}!", is_question=False),
                    ],
                ),
                Rule(
                    effect=Fact(text="USER says their name", is_question=False),
                    causes=[
                        Fact(text="USER is called {username}", is_question=False),
                        Fact(text="nice to meet you {username}", is_question=False),
                    ],
                ),
            ]
        )
        assert str(facts_and_rules["rules"]) == expected

    def test_fact_parsing(self):
        facts_and_rules = get_facts_and_rules_from_text(wafl_example)
        expected = str(
            [
                Fact(text="BOT name is Fractalego", is_question=False),
                Fact(text="the user is happy", is_question=False),
            ]
        )
        assert str(facts_and_rules["facts"]) == expected

    def test_knowledge_facts(self):
        knowledge = Knowledge(wafl_example)
        expected = str(Fact(text="the user is happy", is_question=False))
        facts = knowledge.ask_for_facts(Query("how is the user", is_question=True))
        assert str(facts[0]) == expected

    def test_knowledge_rules(self):
        knowledge = Knowledge(wafl_example)
        expected = str(
            Rule(
                effect=Fact(text="USER greets", is_question=False),
                causes=[
                    Fact(text="USER is called {username}", is_question=False),
                    Fact(text="SAY hello to you, {username}!", is_question=False),
                ],
            )
        )
        rules = knowledge.ask_for_rule_backward(
            Query("the user greets you", is_question=False)
        )
        assert str(rules[0]) == expected
