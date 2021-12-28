import pyaudio
import wave

from subprocess import PIPE, run


class PiCoTTSSpeaker:
    _chunk = 1024
    _format = pyaudio.paInt16
    _channels = 1
    _rate = 16000

    def __init__(self, voice="en-GB"):
        self._pyaudio = pyaudio.PyAudio()
        self._voice = voice
        self._cache_file = "out.wav"

    def speak(self, text):
        self.__generate_cached_voice(text)
        self.__play_cache()

    def __generate_cached_voice(self, text):
        command = [
            "pico2wave",
            f"-l{self._voice}",
            f"-w{self._cache_file}",
            f'"{text}"',
        ]
        run(command, stdout=PIPE, stderr=PIPE)

    def __play_cache(self):
        stream = self._pyaudio.open(
            format=self._format,
            channels=self._channels,
            rate=self._rate,
            input=False,
            output=True,
        )

        waveform = wave.open(self._cache_file)
        data = waveform.readframes(self._chunk)
        while data:
            stream.write(data)
            data = waveform.readframes(self._chunk)

        stream.stop_stream()
        stream.close()
