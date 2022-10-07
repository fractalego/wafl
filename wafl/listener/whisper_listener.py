import tempfile

import pyaudio
import time
import numpy as np
import torch.cuda
import whisper

from scipy.io.wavfile import write
from whisper.decoding import DecodingTask
from whisper.tokenizer import get_tokenizer

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
        self._model = whisper.load_model(model_name).to(device)
        self._options = whisper.DecodingOptions(
            fp16=False,
            without_timestamps=True,
            task="transcribe",
            language="en",
            beam_size=2,
        )
        self._hotwords = list()
        self.is_active = False
        self._temp_filename = None

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
        self._temp_filename = tempfile.NamedTemporaryFile(delete=False).name
        write(self._temp_filename, self._rate, waveform)
        audio = whisper.load_audio(self._temp_filename)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(device)

        result = whisper.decode(self._model, mel, self._options)
        transcription = result.text

        if result.no_speech_prob < 0.4:
            self.deactivate()
            return transcription

        return ""

    def get_hotword_if_present(self):
        for hotword in self._hotwords:
            if self.hotword_is_present(hotword):
                return hotword

        return ""

    def hotword_is_present(self, hotword):
        if not tempfile:
            return False

        tokenizer = get_tokenizer(multilingual=False, task="transcribe", language="en")
        hotword_tokens = torch.tensor([tokenizer.encode(f" {hotword}")])
        print("CHECKING FOR", hotword)

        task = DecodingTask(self._model, self._options)
        audio = whisper.load_audio(self._temp_filename)
        audio = whisper.pad_or_trim(audio)
        mel = whisper.log_mel_spectrogram(audio).to(device)
        mel = mel.unsqueeze(0)
        audio_features = task._get_audio_features(mel)
        n_audio = mel.shape[0]
        input_ids = (
            torch.tensor([task._get_initial_tokens()]).expand(n_audio, -1).to(device)
        )
        for _ in range(hotword_tokens.shape[1]):
            logits = self._model.decoder(
                torch.tensor(input_ids), audio_features, kv_cache={}
            )
            new_token = torch.argmax(logits, dim=-1)
            new_token = torch.tensor([[new_token[:, -1]]]).to(device)
            input_ids = torch.cat([input_ids, new_token], dim=-1)

        logprobs = torch.log(torch.softmax(logits, dim=-1))
        sum_logp = 0
        for logp, index in zip(logprobs[0][1:], hotword_tokens[0]):
            sum_logp += logp[index]

        print("SUM_LOGP", sum_logp)
        return sum_logp > -8


def _rms(frame):
    data = np.frombuffer(frame, dtype=np.int16)
    return np.std(data) / len(data)
