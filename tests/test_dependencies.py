import asyncio

from unittest import TestCase
from wafl.events.conversation_events import ConversationEvents
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge


wafl_dependency = """
#using greetings

The user greets
  name = what is the name of the person that is greeting
  the user wants {name} to greet back
  
the user's name is alberto
  the user is italian

""".strip()


class TestDependencies(TestCase):
    def test__knowledge_dependencies_are_populated(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        knowledge = ProjectKnowledge(tmp_filename)
        expected = {
            "/": ["/greetings"],
            "/greetings": ["/facts", "/rules", "/../backward_import"],
            '/greetings/../backward_import': [],
            "/greetings/facts": [],
            "/greetings/rules": [],
        }
        self.assertEqual(expected, knowledge._dependency_dict)

    def test__knowledge_dictionary_is_populated(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        knowledge = ProjectKnowledge(tmp_filename)
        expected = ["/", "/greetings", "/greetings/facts", "/greetings/rules", "/greetings/../backward_import"]
        self.assertEqual(expected, list(knowledge._knowledge_dict.keys()))

    def test__rules_are_called_from_dependency_list(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        interface = DummyInterface(to_utter=["Hello", "albert"])
        knowledge = ProjectKnowledge(tmp_filename)
        conversation_events = ConversationEvents(
            knowledge, interface=interface, code_path=knowledge.get_dependencies_list()
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: Hello, albert!"
        assert interface.get_utterances_list()[-1] == expected

    def test__facts_are_answered_from_dependency_list_one_level_deep(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        interface = DummyInterface(
            to_utter=[
                "How are you doing",
            ]
        )
        conversation_events = ConversationEvents(
            ProjectKnowledge(tmp_filename), interface=interface
        )
        asyncio.run(conversation_events.process_next())
        expected = "well"
        print(interface.get_utterances_list())
        assert expected in interface.get_utterances_list()[-1]

    def test__facts_are_answered_from_dependency_list_two_levels_deep(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        interface = DummyInterface(
            to_utter=[
                "how is the sun",
            ]
        )
        conversation_events = ConversationEvents(
            ProjectKnowledge(tmp_filename), interface=interface
        )
        asyncio.run(conversation_events.process_next())
        expected = "shin"
        print(interface.get_utterances_list())
        assert expected in interface.get_utterances_list()[-1]

    def test__functions_can_be_called_from_a_dependency(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        interface = DummyInterface(
            to_utter=[
                "What time is it",
            ]
        )
        knowledge = ProjectKnowledge(tmp_filename)
        conversation_events = ConversationEvents(
            ProjectKnowledge(tmp_filename),
            interface=interface,
            code_path=knowledge.get_dependencies_list(),
        )
        asyncio.run(conversation_events.process_next())
        expected = "bot: The time is now!"
        assert interface.get_utterances_list()[-1] == expected

    def test__functions_can_be_called_from_a_2_level_deep_dependency(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        interface = DummyInterface(
            to_utter=[
                "My name is Alberto",
            ]
        )
        knowledge = ProjectKnowledge(tmp_filename)
        conversation_events = ConversationEvents(
            ProjectKnowledge(tmp_filename),
            interface=interface,
            code_path=knowledge.get_dependencies_list(),
        )
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        expected = "bot: Ciao!"
        assert interface.get_utterances_list()[-1] == expected

    def test__rules_can_be_imported_using_prior_folders(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        interface = DummyInterface(
            to_utter=[
                "My name is Maria",
            ]
        )
        knowledge = ProjectKnowledge(tmp_filename)
        conversation_events = ConversationEvents(
            ProjectKnowledge(tmp_filename),
            interface=interface,
            code_path=knowledge.get_dependencies_list(),
        )
        asyncio.run(conversation_events.process_next())
        print(interface.get_utterances_list())
        expected = "bot: The sky is green"
        assert interface.get_utterances_list()[-1] == expected
