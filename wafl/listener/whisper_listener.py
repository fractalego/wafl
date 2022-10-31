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

    def __init__(self, model_name):
        self._p = pyaudio.PyAudio()
        self._threshold = 1
        self._timeout = 1
        self._max_timeout = 4
        self._model = WhisperForConditionalGeneration.from_pretrained(model_name).to(
            device
        )
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
                return self.input_waveform(waveform)

    def input_waveform(self, waveform):
        self._last_waveform = waveform
        input_features = self._processor(waveform, return_tensors="pt").input_features
        output = self._model.generate(
            input_features.to(device),
            num_beams=2,
            return_dict_in_generate=True,
            output_scores=True,
        )
        transcription = self._processor.batch_decode(
            output.sequences, skip_special_tokens=True
        )[0]

        if torch.exp(output.sequences_scores) > 0.6:
            self.deactivate()
            return transcription

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
            self._last_waveform, return_tensors="pt"
        ).input_features
        hotword_tokens = torch.tensor([self._processor.tokenizer.encode(f" {hotword}")])
        starting_tokens = [50257, 50362]
        input_ids = torch.tensor([starting_tokens]).to(device)
        for _ in range(hotword_tokens.shape[1]):
            logits = self._model(
                input_features.to(device),
                decoder_input_ids=input_ids,
            ).logits
            new_token = torch.argmax(logits, dim=-1)
            new_token = torch.tensor([[new_token[:, -1]]]).to(device)
            input_ids = torch.cat([input_ids, new_token], dim=-1)

        logprobs = torch.log(torch.softmax(logits, dim=-1))
        sum_logp = 0
        for logp, index in zip(logprobs[0][1:], hotword_tokens[0]):
            sum_logp += logp[index]

        return sum_logp > -8


def _rms(frame):
    data = np.frombuffer(frame, dtype=np.int16)
    return np.std(data) / len(data)
