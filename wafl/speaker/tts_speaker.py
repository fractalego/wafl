import asyncio

import numpy as np
import pyaudio

from wafl.connectors.factories.speaker_connector_factory import SpeakerConnectorFactory
from wafl.speaker.base_speaker import BaseSpeaker
from wafl.speaker.utils import convert_numbers_to_words


class TTSSpeaker(BaseSpeaker):
    def __init__(self, config):
        self._connector = SpeakerConnectorFactory.get_connector(config)
        self._p = pyaudio.PyAudio()
        self._input_chunk_size = 1024
        self._output_chunk_size = 4096
        self._volume_threshold = (
            config.get_value("listener_model")["listener_volume_threshold"] * 1e-4
        )
        self._interruptible = config.get_value("listener_model")["interruptible"]

    async def speak(self, text):
        text = convert_numbers_to_words(text)
        prediction = await self._connector.predict(text)
        wav = prediction["wav"]
        rate = prediction["rate"]
        stream = self._p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=rate,
            input=True,
            output=True,
        )
        stream.start_stream()
        await asyncio.sleep(0.1)
        if self._interruptible:
            for i in range(0, len(wav), self._output_chunk_size):
                inp = stream.read(self._input_chunk_size)
                if _rms(inp) > self._volume_threshold:
                    break
                stream.write(wav[i : i + self._output_chunk_size])
        else:
            stream.write(wav)

        stream.stop_stream()
        stream.close()
        await asyncio.sleep(0.1)


def _rms(frame):
    data = np.frombuffer(frame, dtype=np.float32)
    return np.std(data) / len(data)
