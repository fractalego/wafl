import asyncio
import math

import pyaudio
import time
import numpy as np

from wafl.connectors.factories.whisper_connector_factory import WhisperConnectorFactory


class WhisperListener:
    _chunk = 1024
    _format = pyaudio.paInt16
    _channels = 1
    _rate = 16000
    _range = 32768
    _generation_max_length = 15
    _starting_tokens = [50257, 50362]
    _ending_tokens = [50256]

    def __init__(self, config):
        self._p = pyaudio.PyAudio()
        self._volume_threshold = 1
        self._original_volume_threshold = self._volume_threshold
        self._timeout = 1
        self._max_timeout = 4
        self._hotword_threshold = -8
        self._connector = WhisperConnectorFactory.get_connector(config)
        self._hotwords = list()
        self.is_active = False
        self._last_waveform = None

    def set_hotwords(self, hotwords):
        self._hotwords = [item.lower() for item in hotwords]

    def add_hotwords(self, hotwords):
        if hotwords and not type(hotwords) == list:
            hotwords = [hotwords]

        self._hotwords.extend([item.lower() for item in hotwords])

    def set_timeout(self, timeout):
        self._timeout = timeout

    def set_volume_threshold(self, threshold):
        self._volume_threshold = threshold
        self._original_volume_threshold = self._volume_threshold

    def set_hotword_threshold(self, threshold):
        self._hotword_threshold = threshold

    def record(self, start_with):
        rec = list()
        rec.append(start_with)

        current = time.time()
        end = time.time() + self._timeout
        upper_limit_end = time.time() + self._max_timeout

        while current <= end and current < upper_limit_end:
            data = self.stream.read(self._chunk)
            if _rms(data) >= self._volume_threshold:
                end = time.time() + self._timeout

            current = time.time()
            rec.append(data)

        return np.frombuffer(b"".join(rec), dtype=np.int16) / self._range

    def activate(self):
        if not self.is_active:
            self.stream = self._p.open(
                format=self._format,
                channels=self._channels,
                rate=self._rate,
                input=True,
                output=False,
                frames_per_buffer=self._chunk,
            )
            self.is_active = True

    def deactivate(self):
        if self.is_active:
            self.stream.stop_stream()
            self.stream.close()
            self.is_active = False

    async def input(self):
        if not self.is_active:
            self.activate()

        while True:
            await asyncio.sleep(0)
            try:
                inp = self.stream.read(self._chunk)
            except IOError:
                self.activate()
                inp = self.stream.read(self._chunk)

            rms_val = _rms(inp)
            if rms_val > self._volume_threshold:
                waveform = self.record(start_with=inp)
                self.deactivate()
                return await self.input_waveform(waveform)

            else:
                new_threshold = 2 * rms_val
                self._volume_threshold = max(
                    new_threshold, self._original_volume_threshold
                )

    async def input_waveform(self, waveform):
        self._last_waveform = waveform
        prediction = await self._connector.predict(waveform)
        transcription = prediction["transcription"]
        score = prediction["score"]

        if math.exp(score) > 0.5:
            return transcription

        return "[unclear]"

    async def get_hotword_if_present(self):
        for hotword in self._hotwords:
            if await self.hotword_is_present(hotword):
                return hotword

        return ""

    async def hotword_is_present(self, hotword):
        if type(self._last_waveform) != np.ndarray:
            raise RuntimeError(
                "The waveform has not been processed. Please call input_waveform() before hotword_is_present()"
            )
        prediction = await self._connector.predict(self._last_waveform, hotword=hotword)
        return prediction["logp"] > self._hotword_threshold


def _rms(frame):
    data = np.frombuffer(frame, dtype=np.int16)
    return np.std(data) / len(data)
