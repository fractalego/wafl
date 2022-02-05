import os
import wave
from unittest import TestCase

import numpy as np

from wafl.conversation.conversation import Conversation
from wafl.inference.backward_inference import BackwardInference
from wafl.interface.dummy_interface import DummyInterface
from wafl.knowledge.knowledge import Knowledge
from wafl.listener.wav2vec2_listener import Wav2Vec2Listener
from wafl.qa.qa import Query

_path = os.path.dirname(__file__)


class TestNew(TestCase):
    pass
