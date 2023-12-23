import logging
import re


from wafl.connectors.utils import select_best_answer

_system_logger = logging.getLogger(__file__)

model = None
tokenizer = None


class BaseLLMConnector:
    _max_tries = 3
    _max_reply_length = 500
    _num_prediction_tokens = 200
    _cache = {}

    def __init__(self, last_strings=None):
        if not last_strings:
            self._last_strings = [
                "\nuser",
                "\nbot",
                "<|EOS|>",
                "</remember>",
                "</execute>\n",
                "</s>",
            ]

        else:
            self._last_strings = last_strings

    async def predict(self, prompt: str) -> [str]:
        raise NotImplementedError

    async def generate(self, prompt: str) -> str:
        if prompt in self._cache:
            return self._cache[prompt]

        text = prompt
        start = len(text)
        while (
            all(item not in text[start:] for item in self._last_strings)
            and len(text) < start + self._max_reply_length
        ):
            text += select_best_answer(await self.predict(text), self._last_strings)

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

        if not candidate_answer:
            candidate_answer = "unknown"

        return candidate_answer
