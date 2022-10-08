from unittest import TestCase

from wafl.conversation.conversation import Conversation
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.parsing.preprocess import (
    create_preprocessed,
    remove_preprocessed,
    import_module,
    get_all_functions_names,
)

wafl_example = """
  
the user says hello
  c()
  
"""



class TestLanguageInFunctions(TestCase):
    def test__preprocessing_has_all_functions_names(self):
        predicted = get_all_functions_names("preprocess_test_functions")
        expected = ["a", "b", "c"]
        assert predicted == expected

    def test__preprocessing_runs(self):
        create_preprocessed("preprocess_test_functions")
        remove_preprocessed("preprocess_test_functions")

    def test__import_preprocessed_module(self):
        create_preprocessed("preprocess_test_functions")
        import_module("preprocess_test_functions")
        remove_preprocessed("preprocess_test_functions")

    def test__functions_can_call_another_function(self):
        interface = DummyInterface(
            to_utter=[
                "Hello",
            ]
        )
        conversation = Conversation(
            Knowledge(wafl_example), interface=interface, code_path="preprocess_test_functions"
        )
        conversation.input()
        expected = [
            "Hello",
        ]
        assert interface.utterances == expected
        
