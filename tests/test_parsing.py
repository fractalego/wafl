from unittest import TestCase

from wafl.facts import Fact
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.parsing.rules_parser import get_facts_and_rules_from_text, get_dependency_list
from wafl.qa.dataclasses import Query
from wafl.rules import Rule

wafl_example = """
#using lists, tfl
#using weather

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
    def test__rules_parsing(self):
        facts_and_rules = get_facts_and_rules_from_text(wafl_example)
        expected = str(
            [
                Rule(
                    effect=Fact(
                        text="USER greets",
                        is_question=False,
                        variable=None,
                        is_interruption=False,
                        source=None,
                        destination=None,
                        knowledge_name=None,
                    ),
                    causes=[
                        Fact(
                            text="USER is called {username}",
                            is_question=False,
                            variable=None,
                            is_interruption=False,
                            source=None,
                            destination=None,
                            knowledge_name=None,
                        ),
                        Fact(
                            text="SAY hello to you, {username}!",
                            is_question=False,
                            variable=None,
                            is_interruption=False,
                            source=None,
                            destination=None,
                            knowledge_name=None,
                        ),
                    ],
                    knowledge_name="/",
                ),
                Rule(
                    effect=Fact(
                        text="USER says their name",
                        is_question=False,
                        variable=None,
                        is_interruption=False,
                        source=None,
                        destination=None,
                        knowledge_name=None,
                    ),
                    causes=[
                        Fact(
                            text="USER is called {username}",
                            is_question=False,
                            variable=None,
                            is_interruption=False,
                            source=None,
                            destination=None,
                            knowledge_name=None,
                        ),
                        Fact(
                            text="nice to meet you {username}",
                            is_question=False,
                            variable=None,
                            is_interruption=False,
                            source=None,
                            destination=None,
                            knowledge_name=None,
                        ),
                    ],
                    knowledge_name="/",
                ),
            ]
        )
        print(str(facts_and_rules["rules"]))
        assert str(facts_and_rules["rules"]) == expected

    def test__fact_parsing(self):
        facts_and_rules = get_facts_and_rules_from_text(wafl_example)
        expected = str(
            [
                Fact(
                    text="BOT name is Fractalego",
                    is_question=False,
                    variable=None,
                    is_interruption=False,
                    source=None,
                    destination=None,
                    knowledge_name=None,
                ),
                Fact(
                    text="the user is happy",
                    is_question=False,
                    variable=None,
                    is_interruption=False,
                    source=None,
                    destination=None,
                    knowledge_name=None,
                ),
            ]
        )
        print(str(facts_and_rules["facts"]))
        assert str(facts_and_rules["facts"]) == expected

    def test__knowledge_facts(self):
        knowledge = SingleFileKnowledge(wafl_example)
        expected = str(Fact(text="the user is happy", is_question=False))
        facts = knowledge.ask_for_facts(Query("how is the user", is_question=True))
        assert str(facts[0]) == expected

    def test__knowledge_rules(self):
        knowledge = SingleFileKnowledge(wafl_example)
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
        print(rules[0])
        assert str(rules[0]) == expected

    def test__dependency_list_is_extracted(self):
        dependency_list = get_dependency_list(wafl_example)
        expected = ["lists", "tfl", "weather"]
        self.assertEqual(dependency_list, expected)
