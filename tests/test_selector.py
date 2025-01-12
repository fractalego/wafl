import os

from unittest import IsolatedAsyncioTestCase
from wafl.config import Configuration
from wafl.connectors.prompt_template import PromptCreator
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector
from wafl.interface.conversation import Conversation, Utterance
from wafl.selectors.selector import Selector

_path = os.path.dirname(__file__)

_prompt_text = """
A user is chatting with a bot. The chat is happening through a web interface. The user is typing the messages and the bot is replying.

This is summary of the bot's knowledge:
{facts}

The rules that *must* be followed are:
{rules}

Create a plausible dialogue based on the aforementioned summary and rules.
Do not repeat yourself. Be friendly but not too servile.
Follow the rules if present and they apply to the dialogue. Do not improvise if rules are present.
The user query might be incomplete or ambiguous or ungrammatical. The bot *must* ask for clarification if needed.
The bot only answers if the query is clear and unambiguous.
""".strip()

no_rules_texts = """
The user wants to know the time:
  - output <execute>get_time()</execute>.

The user wants to know today's date:
  - output <execute>get_date()</execute>.

The user wants to know the day of the week:
  - output <execute>get_day()</execute>.
""" #### this much faster - the model only generates the output. it does not try to be chatty

rules_texts = """
- the user wants to know the time:
  - output "The time is <execute>get_time()</execute>".

- the user wants to know today's date:
  - output "The date is <execute>get_date()</execute>".

- the user wants to know today's day of the week:
  - output "The day of the week is <execute>get_day()</execute>".
"""


class TestSelector(IsolatedAsyncioTestCase):
    async def test__selector_execute_time_function_due_to_rules(self):
        config = Configuration.load_local_config()
        config.set_value("generation_config", {"temperature": 0.5, "num_replicas": 3})
        connector = RemoteLLMConnector(config)
        conversation = Conversation(
            [Utterance("What time is it?", "user")]
        )
        prompt_template = PromptCreator.create_from_arguments(
            prompt=_prompt_text,
            conversation=conversation,
            facts="",
            rules=rules_texts,

        )
        answer_list = await connector.generate(prompt_template)
        print(answer_list)
        prediction = await Selector(config).select_best_answer(
            memory="",
            rules_text_list=[rules_texts],
            conversation=conversation,
            answers=answer_list,
        )
        expected = "<execute>get_time()"
        print(prediction)
        self.assertIn(expected, prediction)

    async def test__selector_execute_date_function_due_to_rules(self):
        config = Configuration.load_local_config()
        config.set_value("generation_config", {"temperature": 0.5, "num_replicas": 3})
        connector = RemoteLLMConnector(config)
        conversation = Conversation(

            [Utterance("What date is today?", "user")]
        )
        prompt_template = PromptCreator.create_from_arguments(
            prompt=_prompt_text,
            conversation=conversation,
            facts="",
            rules=rules_texts,

        )
        answer_list = await connector.generate(prompt_template)
        print(answer_list)
        prediction = await Selector(config).select_best_answer(
            memory="",
            rules_text_list=[rules_texts],
            conversation=conversation,
            answers=answer_list,
        )
        expected = "<execute>get_date()"
        print(prediction)
        self.assertIn(expected, prediction)
