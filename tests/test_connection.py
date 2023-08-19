import asyncio
import os
import wave

from unittest import TestCase

import numpy as np

from wafl.config import Configuration
from wafl.connectors.llm_chitchat_answer_bridge import LLMChitChatAnswerBridge
from wafl.connectors.local_entailment_connector import LocalEntailmentConnector
from wafl.connectors.local_llm_connector import LocalLLMConnector
from wafl.connectors.local_whisper_connector import LocalWhisperConnector
from wafl.connectors.remote_llm_connector import RemoteLLMConnector
from wafl.connectors.llm_qa_connector import LLMQAConnector
from wafl.extractors.entailer import Entailer
from wafl.listener.whisper_listener import WhisperListener

_path = os.path.dirname(__file__)


class TestConnection(TestCase):
    def test__connection_to_generative_model_hostname_is_active(self):
        config = Configuration.load_local_config()
        LLMQAConnector(config)

    def test__connection_to_generative_model_hostname_answer_a_question_correctly(self):
        config = Configuration.load_local_config()
        connector = LLMQAConnector(config)
        answer_text = asyncio.run(
            connector.get_answer(
                text="The bot remembers: The sky is blue",
                dialogue="",
                query="what color is the sky?",
            )
        )
        expected = "blue"
        self.assertEqual(expected, answer_text)

    def test__connection_to_generative_model_can_generate_text(self):
        config = Configuration.load_local_config()
        connector = RemoteLLMConnector(config)
        prediction = asyncio.run(
            connector.predict(
                'Generate a full paragraph based on this chapter title "The first contact". '
                "The theme of the paragraph is space opera. "
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

        prediction = asyncio.run(connector.predict(prompt))
        print(prediction)
        assert len(prediction) > 0

    def test__connection_to_generative_model_can_generate_a_python_list(self):
        config = Configuration.load_local_config()
        connector = RemoteLLMConnector(config)
        connector._num_prediction_tokens = 200
        prompt = "Generate a Python list of 4 chapters names for a space opera book. The output needs to be a python list of strings: "
        prediction = asyncio.run(connector.predict(prompt))
        print(prediction)
        assert len(prediction) > 0

    def test__local_llm_connector_can_generate_a_python_list(self):
        config = Configuration.load_from_filename("local_config.json")
        connector = LocalLLMConnector(config)
        connector._num_prediction_tokens = 200
        prompt = "Generate a Python list of 4 chapters names for a space opera book. The output needs to be a python list of strings: "
        prediction = asyncio.run(connector.predict(prompt))
        assert len(prediction) > 0

    def test__chit_chat_bridge_can_run_locally(self):
        config = Configuration.load_from_filename("local_config.json")
        connector = LocalLLMConnector(config)
        dialogue_bridge = LLMChitChatAnswerBridge(connector)
        answer = asyncio.run(dialogue_bridge.get_answer("", "", "bot: hello"))
        assert len(answer) > 0

    def test__entailment_local_connector(self):
        premise = "The user says 'hello.'."
        hypothesis = "The user is greeting"
        config = Configuration.load_from_filename("local_config.json")
        connector = LocalEntailmentConnector(config)
        entailer = Entailer(connector)
        prediction = asyncio.run(entailer.get_relation(premise, hypothesis))
        self.assertTrue(prediction["entailment"] > 0.95)

    def test__listener_local_connector(self):
        config = Configuration.load_from_filename("local_config.json")
        connector = LocalWhisperConnector(config)
        listener = WhisperListener(connector)
        f = wave.open(os.path.join(_path, "data/1002.wav"), "rb")
        waveform = np.frombuffer(f.readframes(f.getnframes()), dtype=np.int16) / 32768
        result = asyncio.run(listener.input_waveform(waveform))
        print(result)
        expected = "DELETE BATTERIES FROM THE GROCERY LIST"
        assert expected.lower() in result
