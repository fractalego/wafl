import asyncio
from unittest import TestCase

from wafl.config import Configuration
from wafl.testcases import ConversationTestCases

_wafl_example = """
rules:
  - the user says "hello":
    - You must answer the user by writing "Hello. What is your name"
    
  - the user says their name:
    - You must answer the user by writing "nice to meet you, NAME_OF_THE_USER!"
""".strip()


_test_case_greetings = """

test the greetings work
  user: Hello
  bot: Hello there! What is your name
  user: Bob
  bot: Nice to meet you, bob!

! test the greetings uses the correct name
  user: Hello
  bot: Hello there! What is your name
  user: Bob
  bot: Nice to meet you, unknown!


""".strip()


class TestConversationalTestCases(TestCase):
    def test_conversation_testcase_run_all(self):
        config = Configuration.load_local_config()
        config.set_value("rules", _wafl_example)
        testcase = ConversationTestCases(config=config, text=_test_case_greetings)
        self.assertTrue(asyncio.run(testcase.run()))
