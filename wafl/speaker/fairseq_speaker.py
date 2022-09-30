import pyaudio

from fairseq.checkpoint_utils import load_model_ensemble_and_task_from_hf_hub
from fairseq.models.text_to_speech.hub_interface import TTSHubInterface
from wafl.speaker.base_speaker import BaseSpeaker


class FairSeqSpeaker(BaseSpeaker):
    def __init__(self, voice="facebook/fastspeech2-en-ljspeech"):
        self._chunk = 1024
        models, cfg, self._task = load_model_ensemble_and_task_from_hf_hub(
            voice, arg_overrides={"vocoder": "hifigan", "fp16": False}
        )
        self._p = pyaudio.PyAudio()
        self._model = models[0]
        TTSHubInterface.update_cfg_with_data_cfg(cfg, self._task.data_cfg)
        self._generator = self._task.build_generator(models, cfg)
        self._generator.vocoder.model.cpu()

    def speak(self, text):
        sample = TTSHubInterface.get_model_input(self._task, text)
        wav, rate = TTSHubInterface.get_prediction(
            self._task, self._model, self._generator, sample
        )

        stream = self._p.open(
            format=pyaudio.paFloat32,
            channels=1,
            rate=rate,
            output=True,
        )
        stream.write(wav.numpy().tobytes())
        stream.stop_stream()
        stream.close()
