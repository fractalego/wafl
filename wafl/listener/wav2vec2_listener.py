import os
import pyaudio
import time
import numpy as np

from transformers import Wav2Vec2ForCTC, Wav2Vec2Processor
from pyctcdecode import build_ctcdecoder

os.environ["TOKENIZERS_PARALLELISM"] = "false"


class Wav2Vec2Listener:
    _chunk = 1024
    _format = pyaudio.paInt16
    _channels = 1
    _rate = 16000
    _range = 32768

    def __init__(self, model_name):
        self._p = pyaudio.PyAudio()
        self._threshold = 1
        self._timeout = 1
        self._max_timeout = 4
        self._processor = Wav2Vec2Processor.from_pretrained(model_name)
        self._model = Wav2Vec2ForCTC.from_pretrained(model_name)
        self._hotwords = list()
        self._decoder = build_ctcdecoder(
            [k for k, _ in self._processor.tokenizer.get_vocab().items()],
            alpha=0.5,
            beta=1.0,
        )
        self.is_active = False

    def set_hotwords(self, hotwords):
        self._hotwords = hotwords

    def add_hotwords(self, hotwords):
        print("Interface: adding hotwords", str(hotwords))
        self._hotwords += hotwords

    def set_timeout(self, timeout):
        self._timeout = timeout

    def set_threshold(self, threshold):
        self._threshold = threshold

    def record(self, start_with):
        rec = list()
        rec.append(start_with)

        current = time.time()
        end = time.time() + self._timeout
        upper_limit_end = time.time() + self._max_timeout

        while current <= end and current < upper_limit_end:
            data = self.stream.read(self._chunk)
            if _rms(data) >= self._threshold:
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

    def input(self):
        if not self.is_active:
            self.activate()

        while True:
            inp = self.stream.read(self._chunk)
            rms_val = _rms(inp)
            if rms_val > self._threshold:
                waveform = self.record(start_with=inp)
                input_values = self._processor(
                    waveform,
                    return_tensors="pt",
                    padding="longest",
                    sampling_rate=self._rate,
                ).input_values
                logits = self._model(input_values).logits
                print(self._hotwords)
                transcription = self._decoder.decode(
                    logits.cpu().detach().numpy()[0],
                    hotwords=self._hotwords,
                    hotword_weight=10.0,
                )
                if len(transcription) >= 2:
                    self.deactivate()
                    return transcription


def _rms(frame):
    data = np.frombuffer(frame, dtype=np.int16)
    return np.std(data) / len(data)
