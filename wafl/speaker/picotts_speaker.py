from time import sleep

import pyaudio
from picotts import PicoTTS


class PiCoTTSSpeaker:
    def __init__(self, voice="en-GB"):
        self._picotts = PicoTTS()
        self._picotts.voice = voice
        self._pyaudio = pyaudio.PyAudio()
        self._stream = self._pyaudio.open(
            format=pyaudio.paInt16, channels=1, rate=16000, input=False, output=True
        )

    def speak(self, text):
        waveform = self._picotts.synth_wav(text)
        self._stream.write(waveform[100:])
