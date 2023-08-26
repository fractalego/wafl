import asyncio

from unittest import TestCase

from wafl.config import Configuration
from wafl.connectors.bridges.llm_code_creator_bridge import LLMCodeCreatorBridge
from wafl.connectors.bridges.llm_task_creator_bridge import LLMTaskCreatorBridge
from wafl.events.conversation_events import ConversationEvents
from wafl.extractors.code_creator import CodeCreator
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
        config = Configuration.load_local_config()
        connector = LLMTaskCreatorBridge(config)
        task = "the user wants to go swimming in the sea"
        triggers = "\n".join(
            [
                "- the user wants to know the road to somewhere",
                "- the user wants to say hello",
            ]
        )
        prediction = asyncio.run(connector.get_answer("", triggers, task))
        expected = """
the user wants to go swimming in the sea
   location = where do you want to go?
   result = Answer the following question. How to get to {location}?
   SAY This is the road to {location}: {result}
        """.strip()
        print(prediction)
        assert expected == prediction

    def test__task_creation1(self):
        config = Configuration.load_local_config()
        knowledge = SingleFileKnowledge(config, _wafl_example)
        task_creator = TaskCreator(config, knowledge)
        task = "the user wants to go swimming in the sea at brighton beach"
        answer = asyncio.run(task_creator.extract(task))
        expected = """
the user wants to go swimming in the sea at brighton beach
   road_to_brighton_beach = the user wants to know the road to brighton beach
   weather = the user wants to know the weather
   result = Answer the following question given this road and weather: {road_to_brighton_beach}. How to get to brighton beach?
   SAY {result}
        """.strip()
        print(answer.text)
        assert expected == answer.text.strip()

    def test__task_creation2(self):
        config = Configuration.load_local_config()
        knowledge = SingleFileKnowledge(config, _wafl_example)
        task_creator = TaskCreator(config, knowledge)
        task = "the user wants to know if they need and umbrella"
        answer = asyncio.run(task_creator.extract(task))
        expected = """
the user wants to know if they need an umbrella
   weather_forecast = the user wants to know the weather
   result = Answer the following question given this forecast: {weather_forecast}. Do you need an umbrella?
   SAY {result}
        """.strip()
        print(answer.text)
        assert expected == answer.text.strip()

    def test__task_creation3(self):
        config = Configuration.load_local_config()
        knowledge = SingleFileKnowledge(config, _wafl_example)
        task_creator = TaskCreator(config, knowledge)
        task = "the user wants to go from London to Manchester"
        answer = asyncio.run(task_creator.extract(task))
        expected = """
the user wants to go from London to Manchester
   road_to_manchester = the user wants to know the road to Manchester
   result = Answer the following question given this road: {road_to_manchester}. How to get to Manchester?
   SAY {result}
    """.strip()
        print(answer.text)
        assert expected == answer.text.strip()

    def test__task_is_created_from_conversation(self):
        interface = DummyInterface(to_utter=["Tell me if I need an umbrella"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            ProjectKnowledge.create_from_string(
                config, _wafl_example, knowledge_name="/"
            ),
            interface=interface,
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: The probability of rain is 95%. you should bring an umbrella."
        print(interface.get_utterances_list())
        assert interface.get_utterances_list()[-1] == expected

    def test__code_creation(self):
        config = Configuration.load_local_config()
        connector = LLMCodeCreatorBridge(config)
        task = "connect to 'localhost:port' and return the data as json"
        function_shape = "json_data = connect_to_localhost(port)"
        prediction = asyncio.run(connector.get_answer("", function_shape, task))
        expected = """
def connect_to_localhost(port):
    import socket
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((socket.gethostname(), port))
    return s.recv(1024).decode('utf-8')
        """.strip()
        print(prediction)
        assert expected == prediction

    def test__task_creation_with_function(self):
        config = Configuration.load_local_config()
        knowledge = SingleFileKnowledge(config, _wafl_example)
        code_creator = CodeCreator(config, knowledge)
        task = "folders_list = list_subfolders('/var/') <the user wants list all the subfolders in a folder>"
        answer = asyncio.run(code_creator.extract(task))
        expected = """
def list_subfolders(folder_name):
    import os

    subfolders = []
    for subfolder in os.listdir(folder_name):
        if os.path.isdir(os.path.join(folder_name, subfolder)):
            subfolders.append(subfolder)
    return subfolders
            """.strip()
        print(answer.text)
        assert expected == answer.text.strip()

    def test__task_is_created_from_conversation_with_code(self):
        interface = DummyInterface(to_utter=["Please list of the subfolders of /var"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            ProjectKnowledge.create_from_string(
                config, _wafl_example, knowledge_name="/"
            ),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        assert "bot: tmp" in [item.lower() for item in interface.get_utterances_list()]
        assert "bot: lib" in [item.lower() for item in interface.get_utterances_list()]

    def test__math_task_is_created_from_conversation(self):
        interface = DummyInterface(to_utter=["Multiply 100 and 43"])
        config = Configuration.load_local_config()
        conversation_events = ConversationEvents(
            ProjectKnowledge.create_from_string(
                config, _wafl_example, knowledge_name="/"
            ),
            interface=interface,
            code_path="/",
        )
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        assert "4300" in interface.get_utterances_list()[-1]
