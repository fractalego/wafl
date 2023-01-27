import asyncio
import os

from unittest import TestCase

from wafl.events.conversation_events import ConversationEvents
from wafl.events.generated_events import GeneratedEvents
from wafl.generators.generator_from_module_name import GeneratorFromModuleName
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_path = os.path.dirname(__file__)
_wafl_example = """
the user wants to set an alarm at a specific time
  time = At what time?
  REMEMBER the time is {time} :- SAY Hello there!; SAY This rule was created
  SAY An alarm was created for {time}
  
the user wants to set an alarm in minutes from now
  minutes_from_now = how many minutes from now?
  time = get_time_in_future(minutes_from_now)
  REMEMBER the time is {time} :- SAY Hello there!; SAY This rule was created
  SAY An alarm was created in {minutes_from_now} minutes
"""


class TestReminders(TestCase):
    def test__time_reminder_can_be_set(self):
        interface = DummyInterface()
        knowledge = SingleFileKnowledge(_wafl_example)
        generated_events = GeneratedEvents(
            knowledge,
            generators=GeneratorFromModuleName("events"),
            interface=interface,
        )
        conversation_events = ConversationEvents(
            knowledge,
            interface=interface,
        )
        input_from_user = "I want an alarm for 7,05"
        asyncio.run(conversation_events._process_query(input_from_user))
        expected = "bot: An alarm was created for 7,05"
        assert interface.get_utterances_list()[-1] == expected

        asyncio.run(generated_events.process_next())
        expected = ["bot: Hello there!", "bot: This rule was created"]
        assert interface.get_utterances_list()[-2:] == expected

    def test__time_reminder_can_be_set_1_minute_from_now(self):
        interface = DummyInterface()
        knowledge = SingleFileKnowledge(_wafl_example)
        generated_events = GeneratedEvents(
            knowledge,
            generators=GeneratorFromModuleName("events"),
            interface=interface,
        )
        conversation_events = ConversationEvents(
            knowledge,
            interface=interface,
            code_path="/"
        )
        input_from_user = "I want to set an alarm in one minute"
        asyncio.run(conversation_events._process_query(input_from_user))
        expected = "bot: An alarm was created in 1 minutes"
        assert interface.get_utterances_list()[-1] == expected

        while not asyncio.run(generated_events.process_next()):
            pass

        expected = ["bot: Hello there!", "bot: This rule was created"]
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-2:] == expected
