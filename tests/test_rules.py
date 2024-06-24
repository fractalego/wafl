import asyncio

from unittest import TestCase

from wafl.config import Configuration
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.parsing.rules_parser import get_facts_and_rules_from_text

wafl_example = """
rules:
  - the user says "my name is bob":
    - You must answer the user by writing "the horse is tall"
    
  - the user says their name:
    - reply casually to the conversation"
    
  - the user wants to buy coffee:
    - the bot says the coffee prices:
        - decaf is 1.50
        - regular is 1.00
        - espresso is 2.00
    - ask for which price range
    - tell them the right coffee
"""


class TestRules(TestCase):
    def test__rules_can_be_triggered(self):
        interface = DummyInterface(
            to_utter=[
                "my name is bob",
            ]
        )
        config = Configuration.load_local_config()
        config.set_value("rules", wafl_example)
        conversation_events = ConversationEvents(
            config=config,
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        expected = "the horse is tall"
        self.assertIn(expected, interface.get_utterances_list()[-1].lower())

    def test__rules_are_not_always_triggered(self):
        interface = DummyInterface(
            to_utter=[
                "my name is Frank",
            ]
        )
        config = Configuration.load_local_config()
        config.set_value("rules", wafl_example)
        conversation_events = ConversationEvents(
            config=config,
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        unexpected = "bot: the horse is tall"
        self.assertNotEqual(unexpected, interface.get_utterances_list()[-1])

    def test__rules_can_nest(self):
        interface = DummyInterface(
            to_utter=[
                "I want to buy coffee",
            ]
        )
        config = Configuration.load_local_config()
        config.set_value("rules", wafl_example)
        conversation_events = ConversationEvents(
            config=config,
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        self.assertIn("decaf", interface.get_facts_and_timestamp()[0][1])
        self.assertIn("regular", interface.get_facts_and_timestamp()[0][1])
        self.assertIn("espresso", interface.get_facts_and_timestamp()[0][1])

    def test__nested_rules_are_printed_correctly(self):
        rule_text = """
rules:        
    - the user wants to know the time:
        - output "The time is <execute>get_time()</execute>":
            - if the time is before 12:00 say "Good morning"
            - if the time is after 12:00 say "Good afternoon"        
        """.strip()

        facts_and_rules = get_facts_and_rules_from_text(rule_text)
        rule = facts_and_rules["rules"][0]
        expected = """
the user wants to know the time
  - output "The time is <execute>get_time()</execute>"
    - if the time is before 12:00 say "Good morning"
    - if the time is after 12:00 say "Good afternoon"        
        """.strip()
        self.assertEqual(expected, str(rule).strip())
