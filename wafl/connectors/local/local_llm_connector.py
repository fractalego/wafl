import logging
import time
import re
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import StoppingCriteria

_system_logger = logging.getLogger(__file__)

device = "cuda" if torch.cuda.is_available() else "cpu"
model = None
tokenizer = None

class LocalLLMConnector:
    _max_tries = 3
    _max_reply_length = 500
    _num_prediction_tokens = 200
    _cache = {}

    def __init__(self, config):
        global model, tokenizer
        if not model:
            _system_logger.info(f"Loading model {config['local_model']} locally.")
            model = AutoModelForCausalLM.from_pretrained(
                config["local_model"],
                init_device=device,
                trust_remote_code=True,
                torch_dtype=torch.half,
            )
            _system_logger.info(f"The model is loaded.")

        if not tokenizer:
            tokenizer = AutoTokenizer.from_pretrained(config["local_model"])

        self._stop_at_eos = StopAtEOS(tokenizer)

    async def predict(self, prompt: str) -> str:
        input_ids = tokenizer.encode(
            prompt, return_tensors="pt", truncation=True, max_length=1008
        ).to(device)
        with torch.no_grad():
            num_beams = 1
            num_tokens = 200
            output = model.generate(
                input_ids,
                max_new_tokens=num_tokens,
                num_beams=num_beams,
                num_return_sequences=1,
                pad_token_id=tokenizer.eos_token_id,
                eos_token_id=tokenizer.eos_token_id,
                use_cache=True,
                stopping_criteria=[self._stop_at_eos],
            )
            output_ids = list(output[0][input_ids.shape[1] :])
            if tokenizer.eos_token_id in output_ids:
                output_ids = output_ids[: output_ids.index(tokenizer.eos_token_id)]

            answer = tokenizer.decode(output_ids)
            answer = re.sub(r"(.*)<\|.*\|>(.*)", r"\1<|EOS|>", answer)
            answer = re.sub(r"(.*)#", r"\1<|EOS|>", answer)

        return answer

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
                for item in ["<|EOS|>", "user:", "\nThe bot", "bot:"]
            )
            and len(text) < start + self._max_reply_length
        ):
            text += await self.predict(text)

        end_set = set()
        end_set.add(text.find("\nuser:", start))
        end_set.add(text.find("\nbot:", start))
        end_set.add(text.find("<|EOS|>", start))
        end_set.add(text.find("\nThe bot", start))
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
    def __init__(self, tokenizer, last_string="<|EOS|>"):
        self._tokenizer = tokenizer
        self._last_string = last_string

    def __call__(
        self, input_ids: torch.LongTensor, scores: torch.FloatTensor, **kwargs
    ) -> bool:
        generated_text = self._tokenizer.decode(input_ids[0], skip_special_tokens=True)
        return generated_text.rfind(self._last_string) == len(generated_text) - len(
            self._last_string
        )
