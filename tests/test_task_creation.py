import asyncio
from unittest import TestCase
from wafl.connectors.llm_task_creator_connector import LLMTaskCreatorConnector


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
