import torch

from typing import Dict
from fairseq.checkpoint_utils import load_model_ensemble_and_task_from_hf_hub
from fairseq.models.text_to_speech.hub_interface import TTSHubInterface

_device = "cuda" if torch.cuda.is_available() else "cpu"


class LocalSpeakerConnector:
    def __init__(self, config):
        model_name = config["local_model"]
        global model
        models, cfg, self._task = load_model_ensemble_and_task_from_hf_hub(
            model_name,
            arg_overrides={"vocoder": "hifigan", "fp16": False},
        )
        self._model = models[0]
        TTSHubInterface.update_cfg_with_data_cfg(cfg, self._task.data_cfg)
        self._generator = self._task.build_generator(models, cfg)
        self._generator.model.to(_device)
        self._generator.vocoder.model.to(_device)

    async def predict(self, text: str) -> Dict[str, float]:
        sample = TTSHubInterface.get_model_input(self._task, text)
        sample["net_input"]["src_tokens"] = sample["net_input"]["src_tokens"].to(
            _device
        )
        with torch.no_grad():
            wav, rate = TTSHubInterface.get_prediction(
                self._task, self._model, self._generator, sample
            )
        wav = wav.cpu().numpy().tobytes()
        return {"wav": wav, "rate": rate}
