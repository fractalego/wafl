import asyncio
import os

from unittest import TestCase

from wafl.config import Configuration
from wafl.connectors.llm_qa_connector import GPTJQAConnector

_path = os.path.dirname(__file__)


class TestConnection(TestCase):
    def test__connection_to_generative_model_hostname_is_active(self):
        config = Configuration.load_local_config()
        GPTJQAConnector(config)

    def test__connection_to_generative_model_hostname_answer_a_question_correctly(self):
        config = Configuration.load_local_config()
        connector = GPTJQAConnector(config)
        answer_text = asyncio.run(
            connector.get_answer(
                text="The sky is blue", dialogue="", query="what color is the sky?"
            )
        )
        expected = "blue"
        self.assertEqual(expected, answer_text)
