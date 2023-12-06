import logging
import time
import re
from typing import List

import torch

from transformers import AutoTokenizer, AutoModelForCausalLM, AutoConfig
from transformers import StoppingCriteria

from wafl.connectors.utils import select_best_answer

_system_logger = logging.getLogger(__file__)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = None
tokenizer = None


class LocalLLMConnector:
    _max_tries = 3
    _max_reply_length = 500
    _num_prediction_tokens = 200
    _cache = {}

    def __init__(self, config, last_strings=None):
        global model, tokenizer
        if not model:
            _system_logger.info(f"Loading model {config['local_model']} locally.")
            model_name = config["local_model"]
            model = AutoModelForCausalLM.from_pretrained(
                model_name,
                config=AutoConfig.from_pretrained(model_name, trust_remote_code=True),
                torch_dtype=torch.half,
                trust_remote_code=True,
                device_map=device
            )
            if device == "cuda":
               model = torch.compile(model)

            model.eval()
            _system_logger.info(f"The model is loaded.")


        if not last_strings:
            self._last_strings = ["\nuser", "\nbot", "<|EOS|>", "</remember>", "</execute>\n", "</execute>\n", "</s>"]

        else:
            self._last_strings = last_strings

        if not tokenizer:
            model_name = config["local_model"]
            tokenizer = AutoTokenizer.from_pretrained(model_name, padding_side="left")
            tokenizer.truncation_side = "left"

        self._stop_at_eos = StopAtEOS(tokenizer, self._last_strings)

    async def predict(self, prompt: str) -> str:
        input_ids = tokenizer.encode(
            prompt, return_tensors="pt", truncation=True, max_length=1008
        ).to(device)
        num_replicas = 3
        with torch.no_grad():
            input_ids = torch.cat([input_ids] * num_replicas, dim=0)
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

        return select_best_answer(answers)

    async def generate(self, prompt: str) -> str:
        print(__name__)
        start_time = time.time()
        if prompt in self._cache:
            print(time.time() - start_time)
            return self._cache[prompt]

        text = prompt
        start = len(text)
        while (
            all(
                item not in text[start:]
                for item in self._last_strings
            )
            and len(text) < start + self._max_reply_length
        ):
            text += await self.predict(text)

        end_set = set()
        for item in self._last_strings:
            if "</remember>" in item or "</execute>" in item:
                continue

            end_set.add(text.find(item, start))

        if -1 in end_set:
            end_set.remove(-1)

        end = len(text)
        if end_set:
            end = min(end_set)

        candidate_answer = text[start:end].split("bot: ")[-1].strip()
        candidate_answer = re.sub(r"(.*)<\|.*\|>", r"\1", candidate_answer).strip()

        if prompt not in self._cache:
            self._cache[prompt] = candidate_answer

        print(time.time() - start_time)
        if not candidate_answer:
            candidate_answer = "unknown"

        return candidate_answer


class StopAtEOS(StoppingCriteria):
    def __init__(self, tokenizer: "AutoTokenizer", last_strings: List[str]):
        self._tokenizer = tokenizer
        self._last_strings = last_strings

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs
    ) -> bool:
        num_ending_tokens = 0
        max_endings = input_ids.shape[0]
        for token_ids in input_ids:
            generated_text = self._tokenizer.decode(token_ids)
            for last_string in self._last_strings:
                if generated_text.endswith(last_string):
                    num_ending_tokens += 1
                    break

            if num_ending_tokens >= max_endings:
                return True

        return False

