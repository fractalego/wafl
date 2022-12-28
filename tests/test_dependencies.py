from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.project_knowledge import ProjectKnowledge


wafl_dependency = """
#using greetings

The user greets
  person = who is greeting
  the user wants {person} to greet back

""".strip()


class TestDependencies(TestCase):
    def test__knowledge_dependencies_are_populated(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        knowledge = ProjectKnowledge(tmp_filename)
        expected = {
            "/": ["/greetings"],
            "/greetings": ["/facts"],
            "/greetings/facts": [],
        }
        self.assertEqual(expected, knowledge._dependency_dict)

    def test__knowledge_dictionary_is_populated(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        knowledge = ProjectKnowledge(tmp_filename)
        expected = ["/", "/greetings", "/greetings/facts"]
        self.assertEqual(expected, list(knowledge._knowledge_dict.keys()))

    def test__rules_are_called_from_dependency_list(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        interface = DummyInterface(
            to_utter=[
                "Hello my name is Albert",
            ]
        )
        conversation = Conversation(ProjectKnowledge(tmp_filename), interface=interface)
        conversation.input()
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
        conversation = Conversation(ProjectKnowledge(tmp_filename), interface=interface)
        conversation.input()
        expected = "bot: doing well"
        assert interface.get_utterances_list()[-1] == expected

    def test__facts_are_answered_from_dependency_list_two_levels_deep(self):
        tmp_filename = "test.wafl"
        with open(tmp_filename, "w") as file:
            file.write(wafl_dependency)

        interface = DummyInterface(
            to_utter=[
                "how is the sun",
            ]
        )
        conversation = Conversation(ProjectKnowledge(tmp_filename), interface=interface)
        conversation.input()
        expected = "bot: shiny"
        assert interface.get_utterances_list()[-1] == expected

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
        conversation = Conversation(
            ProjectKnowledge(tmp_filename),
            interface=interface,
            code_path=knowledge.get_dependencies_list(),
        )
        conversation.input()
        expected = "bot: The time is now!"
        assert interface.get_utterances_list()[-1] == expected
