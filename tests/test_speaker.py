import os.path
from unittest import TestCase
from wafl.speaker.fairseq_speaker import FairSeqSpeaker
from wafl.speaker.soundfile_speaker import SoundFileSpeaker

_wafl_greetings = """
  
""".strip()

_path = os.path.dirname(__file__)

class TestSpeaker(TestCase):
    def test_voice(self):
        speaker = FairSeqSpeaker()
        text = "Hello world"
        speaker.speak(text)

    def test_on_sound(self):
        speaker = SoundFileSpeaker()
        speaker.speak(os.path.join(_path, "../wafl/sounds/activation.wav"))

    def test_off_sound(self):
        speaker = SoundFileSpeaker()
        speaker.speak(os.path.join(_path, "../wafl/sounds/deactivation.wav"))