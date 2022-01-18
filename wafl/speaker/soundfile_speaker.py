import pyaudio
import wave

from wafl.speaker.base_speaker import BaseSpeaker


class SoundFileSpeaker(BaseSpeaker):
    _chunk = 1024

    def __init__(self):
        self._p = pyaudio.PyAudio()

    def speak(self, filename):
        self.__play_sound(filename)

    def __play_sound(self, sound_filename):
        f = wave.open(sound_filename, "rb")
        stream = self._p.open(
            format=self._p.get_format_from_width(f.getsampwidth()),
            channels=f.getnchannels(),
            rate=f.getframerate(),
            output=True,
        )
        data = f.readframes(self._chunk)

        while data:
            stream.write(data)
            data = f.readframes(self._chunk)

        stream.stop_stream()
        stream.close()
