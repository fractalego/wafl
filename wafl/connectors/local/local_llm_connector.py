import logging
from typing import List

import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from transformers import StoppingCriteria

from wafl.connectors.base_llm_connector import BaseLLMConnector

_system_logger = logging.getLogger(__file__)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = None
tokenizer = None
tokenizer_with_prefix_space = None


class LocalLLMConnector(BaseLLMConnector):
    _num_replicas = 10

    def __init__(self, config, last_strings=None):
        super().__init__(last_strings)
        global model, tokenizer, tokenizer_with_prefix_space
        if not model:
            _system_logger.info(f"Loading model {config['local_model']} locally.")
            model_name = config["local_model"]
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                config=AutoConfig.from_pretrained(model_name, trust_remote_code=True),
                torch_dtype=torch.half,
                trust_remote_code=True,
                device_map=device,
            )
            if device == "cuda":
                model = torch.compile(model)

            model.eval()
            _system_logger.info(f"The model is loaded.")

        if not tokenizer:
            model_name = config["local_model"]
            tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
            tokenizer.truncation_side = "left"

        if not tokenizer_with_prefix_space:
            model_name = config["local_model"]
            tokenizer_with_prefix_space = AutoTokenizer.from_pretrained(model_name, add_prefix_space=True)

        self._stop_at_eos = StopAtEOS(tokenizer, self._last_strings)

    async def predict(self, prompt: str) -> [str]:
        input_ids = tokenizer.encode(
            prompt, return_tensors="pt", truncation=True, max_length=1008
        ).to(device)
        with torch.no_grad():
            input_ids = torch.cat([input_ids] * self._num_replicas, dim=0)
            output_ids = model.generate(
                input_ids.cuda(),
                max_new_tokens=self._num_prediction_tokens,
                temperature=0.5,
                do_sample=True,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
                stopping_criteria=[self._stop_at_eos],
            )
            answers = tokenizer.batch_decode(output_ids[:, input_ids.shape[1] :])

        return answers


    def _get_tokens_as_tuple(self, word):
        return tuple(tokenizer_with_prefix_space([word], add_special_tokens=False).input_ids[0])



class StopAtEOS(StoppingCriteria):
    def __init__(self, tokenizer: "AutoTokenizer", last_strings: List[str]):
        self._tokenizer = tokenizer
        self._last_strings = last_strings

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs
    ) -> bool:
        num_ending_tokens = 0
        for token_ids in input_ids:
            generated_text = self._tokenizer.decode(token_ids)
            for last_string in self._last_strings:
                if generated_text.endswith(last_string):
                    num_ending_tokens += 1
                    break

            if num_ending_tokens >= 1:
                return True

        return False
