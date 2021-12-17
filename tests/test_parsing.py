from unittest import TestCase

from wafl.knowledge import Knowledge
from wafl.parser import get_facts_and_rules_from_text

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
        expected = "[Rule(effect='USER greets', causes=['USER is called {username}', 'SAY hello to you, {username}!']), Rule(effect='USER says their name', causes=['USER is called {username}', 'nice to meet you {username}'])]"
        assert str(facts_and_rules['rules']) == expected

    def test_fact_parsing(self):
        facts_and_rules = get_facts_and_rules_from_text(wafl_example)
        expected = "[Fact(text='BOT name is Fractalego'), Fact(text='the user is happy')]"
        assert str(facts_and_rules['facts']) == expected

    def test_knowledge_facts(self):
        knowledge = Knowledge(wafl_example)
        expected = "Fact(text='the user is happy')"
        facts = knowledge.ask_for_facts("how is the user")
        assert str(facts[0]) == expected

    def test_knowledge_rules(self):
        knowledge = Knowledge(wafl_example)
        expected = "Rule(effect='USER greets', causes=['USER is called {username}', 'SAY hello to you, {username}!'])"
        rules = knowledge.ask_for_rule_backward("the user greets you")
        assert str(rules[0]) == expected



