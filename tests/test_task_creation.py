import asyncio
from unittest import TestCase
from wafl.connectors.llm_task_creator_connector import LLMTaskCreatorConnector
from wafl.events.conversation_events import ConversationEvents
from wafl.extractors.task_creator import TaskCreator
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

_wafl_example = """

The user wants to know the road to somewhere
  SAY Looking now

The user wants to know the weather
  SAY The temperature is going to be between 19 and 22
  SAY The probability of rain is 95%

""".strip()


class TestTaskCreation(TestCase):
    def test__task_creation_connector(self):
        connector = LLMTaskCreatorConnector()
        task = "the user wants to go swimming in the sea"
        triggers = "\n".join(
            [
                "- the user wants to know the road to somewhere",
                "- the user has a headache",
            ]
        )
        prediction = asyncio.run(connector.get_answer("", triggers, task))
        expected = """
the user wants to go swimming in the sea
   road_to_sea = the user wants to know the road to the sea
   result = Answer the following question given this road: {road_to_sea} Q: how to get to the sea? A:
   SAY {result}        
        """.strip()
        print(prediction)
        assert expected == prediction

    def test__task_creation1(self):
        knowledge = SingleFileKnowledge(_wafl_example)
        task_creator = TaskCreator(knowledge)
        task = "the user wants to go swimming in the sea"
        answer = asyncio.run(task_creator.extract(task))
        expected = """
the user wants to go swimming in the sea
   road_to_sea = the user wants to know the road to the sea
   result = Answer the following question given this road: {road_to_sea} Q: How to get to the sea? A:
   SAY {result}
        """.strip()
        print(answer.text)
        assert expected == answer.text.strip()

    def test__task_creation2(self):
        knowledge = SingleFileKnowledge(_wafl_example)
        task_creator = TaskCreator(knowledge)
        task = "the user wants to know if they need and umbrella"
        answer = asyncio.run(task_creator.extract(task))
        expected = """
The user wants to know if they need an umbrella
   weather_forecast = the user wants to know the weather today
   result = Answer the following question given this forecast: {weather_forecast}             Q: do I need an umbrella?            A:
   SAY {result}
        """.strip()
        print(answer.text)
        assert expected == answer.text.strip()

    def test__task_is_created_from_conversation(self):
        interface = DummyInterface(to_utter=["Do I need an umbrella"])
        conversation_events = ConversationEvents(
            ProjectKnowledge.create_from_string(_wafl_example, knowledge_name="/"),
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Yes"
        assert interface.get_utterances_list()[-1] == expected
