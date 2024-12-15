import asyncio
import os

from unittest import TestCase
from wafl.config import Configuration
from wafl.connectors.prompt_template import PromptCreator
from wafl.connectors.remote.remote_llm_connector import RemoteLLMConnector

_path = os.path.dirname(__file__)


class TestConnection(TestCase):
    def test__connection_to_generative_model_can_generate_text(self):
        config = Configuration.load_local_config()
        connector = RemoteLLMConnector(config)
        prediction = asyncio.run(
            connector.predict(
                PromptCreator.create_from_one_instruction(
                    'Generate a full paragraph based on this chapter title "The first contact".'
                    "The theme of the paragraph is space opera. "
                )
            )
        )
        assert len(prediction) > 0

    def test__connection_to_generative_model_can_generate_text_within_tags(self):
        config = Configuration.load_local_config()
        connector = RemoteLLMConnector(config)
        connector._num_prediction_tokens = 200
        text = 'Generate a full paragraph based on this chapter title " The First Contact". The theme of the paragraph is space opera. Include the characters "Alberto" and "Maria". Write at least three sentences.'
        prompt = f"""
<task>
Complete the following task and add <|EOS|> at the end: {text}
</task>
<result>
                """.strip()

        prediction = asyncio.run(
            connector.predict(PromptCreator.create_from_one_instruction(prompt))
        )
        print(prediction)
        assert len(prediction) > 0

    def test__connection_to_generative_model_can_generate_a_python_list(self):
        config = Configuration.load_local_config()
        connector = RemoteLLMConnector(config)
        connector._num_prediction_tokens = 200
        prompt = "Generate a Python list of 4 chapters names for a space opera book. The output needs to be a python list of strings: "
        prediction = asyncio.run(
            connector.predict(PromptCreator.create_from_one_instruction(prompt))
        )
        assert len(prediction) > 0
