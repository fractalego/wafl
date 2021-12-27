import pyaudio
from picotts import PicoTTS


class PiCoTTSSpeaker:
    def __init__(self, voice="en-GB"):
        self._pyaudio = pyaudio.PyAudio()
        self._voice = voice

    def speak(self, text):
        picotts = PicoTTS()
        picotts.voice = self._voice
        waveform = picotts.synth_wav(text)
        stream = self._pyaudio.open(
            format=pyaudio.paInt16, channels=1, rate=16000, input=False, output=True
        )
        stream.write(waveform[100:])
        stream.stop_stream()
        stream.close()
        del stream
        del picotts
