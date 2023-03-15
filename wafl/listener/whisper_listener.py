import asyncio

import pyaudio
import time
import numpy as np
import torch.cuda

from transformers import WhisperProcessor, WhisperForConditionalGeneration

device = "cuda" if torch.cuda.is_available() else "cpu"


class WhisperListener:
    _chunk = 1024
    _format = pyaudio.paInt16
    _channels = 1
    _rate = 16000
    _range = 32768
    _generation_max_length = 15
    _starting_tokens = [50257, 50362]

    def __init__(self, model_name):
        self._p = pyaudio.PyAudio()
        self._volume_threshold = 1
        self._original_volume_threshold = self._volume_threshold
        self._timeout = 1
        self._max_timeout = 4
        self._hotword_threshold = -8
        self._model = WhisperForConditionalGeneration.from_pretrained(model_name).to(
            device
        )
        if torch.cuda.is_available():
            self._model.half()

        self._processor = WhisperProcessor.from_pretrained(model_name)
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
            inp = self.stream.read(self._chunk)
            rms_val = _rms(inp)
            if rms_val > self._volume_threshold:
                waveform = self.record(start_with=inp)
                self.deactivate()
                return self.input_waveform(waveform)

            else:
                new_threshold = 2 * rms_val
                self._volume_threshold = max(
                    new_threshold, self._original_volume_threshold
                )

    def input_waveform(self, waveform):
        self._last_waveform = waveform
        input_features = self._processor(
            waveform, return_tensors="pt", sampling_rate=16_000
        ).input_features
        output = self._model.generate(
            input_features.to(device).half(),
            num_beams=3,
            return_dict_in_generate=True,
            output_scores=True,
            max_length=self._generation_max_length,
        )
        transcription = self._processor.batch_decode(
            output.sequences, skip_special_tokens=True
        )[0]

        if torch.exp(output.sequences_scores) > 0.6:
            return transcription

        if torch.exp(output.sequences_scores) > 0.3:
            return "[unclear]"

        return ""

    def get_hotword_if_present(self):
        for hotword in self._hotwords:
            if self.hotword_is_present(hotword):
                return hotword

        return ""

    def hotword_is_present(self, hotword):
        if type(self._last_waveform) != np.ndarray:
            raise RuntimeError(
                "The waveform has not been processed. Please call input_waveform() before hotword_is_present()"
            )

        input_features = self._processor(
            self._last_waveform, return_tensors="pt", sampling_rate=16_000
        ).input_features
        hotword_tokens = torch.tensor([self._processor.tokenizer.encode(f" {hotword}")])

        input_ids = torch.tensor([self._starting_tokens]).to(device)
        for _ in range(hotword_tokens.shape[1]):
            logits = self._model(
                input_features.to(device).half(),
                decoder_input_ids=input_ids,
            ).logits
            new_token = torch.argmax(logits, dim=-1)
            new_token = torch.tensor([[new_token[:, -1]]]).to(device)
            input_ids = torch.cat([input_ids, new_token], dim=-1)

        logprobs = torch.log(torch.softmax(logits, dim=-1))
        sum_logp = 0
        for logp, index in zip(logprobs[0][1:], hotword_tokens[0]):
            sum_logp += logp[index]

        return sum_logp > self._hotword_threshold


def _rms(frame):
    data = np.frombuffer(frame, dtype=np.int16)
    return np.std(data) / len(data)
