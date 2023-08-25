import asyncio
import pyaudio

from wafl.connectors.factories.speaker_connector_factory import SpeakerConnectorFactory
from wafl.speaker.base_speaker import BaseSpeaker
from wafl.speaker.utils import convert_numbers_to_words


class FairSeqSpeaker(BaseSpeaker):
    def __init__(self, config):
        self._connector = SpeakerConnectorFactory.get_connector(config)
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
        await asyncio.sleep(0.2)
        stream.write(wav)
        stream.stop_stream()
        stream.close()
        await asyncio.sleep(0.1)
