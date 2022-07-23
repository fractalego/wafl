import json
import os
import wave
from unittest import TestCase

import numpy as np
from wafl.parsing.rules_parser import get_facts_and_rules_from_text

from wafl.conversation.conversation import Conversation
from wafl.inference.backward_inference import BackwardInference
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.listener.wav2vec2_listener import Wav2Vec2Listener
from wafl.qa.dataclasses import Query

_path = os.path.dirname(__file__)

_rules = """

the user greets
  USER is called {username}
  SAY hello to you, {username}!

The user says their name
  USER is called {username}
  nice to meet you {username}

This bot name is Fractalego

the user is happy

""".strip()


class TestNew(TestCase):
    def test_parsing_has_source_and_destination(self):
        facts_and_rules = get_facts_and_rules_from_text(_rules)
        [print(item) for item in facts_and_rules["facts"]]
        [print(item) for item in facts_and_rules["rules"]]
