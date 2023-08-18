import csv
import joblib
import os
import time
import re
import torch

from transformers import AutoTokenizer, AutoModelForCausalLM
from transformers import StoppingCriteria

from wafl.config import Configuration
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge

device = "cuda" if torch.cuda.is_available() else "cpu"

class LocalLLMConnector:
    _max_tries = 3
    _max_reply_length = 500
    _num_prediction_tokens = 200
    _cache = {}

    def __init__(self, config=None):
        if not config:
            config = Configuration.load_local_config()

        global model, tokenizer
        model = AutoModelForCausalLM.from_pretrained(
            config.get_value("llm_model")["local_model"],
            init_device=device,
            trust_remote_code=True,
            torch_dtype=torch.half,
        )
        tokenizer = AutoTokenizer.from_pretrained(config.get_value("llm_model")["local_model"])

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


    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        print(__name__)
        start_time = time.time()
        prompt = await self._get_answer_prompt(text, query, dialogue)
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

    async def _get_answer_prompt(self, text, query, dialogue=None):
        raise NotImplementedError("_get_answer_prompt() needs to be implemented.")

    async def _load_knowledge_from_file(self, filename, _path=None):
        items_list = []
        with open(os.path.join(_path, f"../data/{filename}.csv")) as file:
            csvreader = csv.reader(file)
            for row in csvreader:
                items_list.append(row[0].strip())

        knowledge = await SingleFileKnowledge.create_from_list(items_list)
        joblib.dump(knowledge, os.path.join(_path, f"../data/{filename}.knowledge"))
        return knowledge


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