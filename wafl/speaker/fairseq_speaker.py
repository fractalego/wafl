import pyaudio

from wafl.connectors.speaker_connector import SpeakerConnector
from wafl.speaker.base_speaker import BaseSpeaker
from wafl.speaker.utils import convert_numbers_to_words


class FairSeqSpeaker(BaseSpeaker):
    def __init__(self):
        self._connector = SpeakerConnector()
        self._p = pyaudio.PyAudio()

    async def speak(self, text):
        text = convert_numbers_to_words(text)
        prediction = await self._connector.predict(text)
        wav = prediction["wav"]
        rate = prediction["rate"]
        stream = self._p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=rate,
            output=True,
        )
        stream.write(wav)
        stream.stop_stream()
        stream.close()
