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

    def __init__(self, important_strings=None):
        if not important_strings:
            self._important_strings = [
                "\nuser",
                "\nbot",
                "<|EOS|>",
                "</remember>",
                "</execute>\n",
                "</s>",
            ]

        else:
            self._important_strings = important_strings

    async def predict(self, prompt: str) -> [str]:
        raise NotImplementedError

    async def generate(self, prompt: "PromptTemplate") -> str:
        if str(prompt.to_dict()) in self._cache:
            return self._cache[str(prompt.to_dict())]

        text = select_best_answer(await self.predict(prompt), self._important_strings)
        end_set = set()
        for item in self._important_strings:
            if "</remember>" in item or "</execute>" in item:
                continue

            end_set.add(text.find(item))

        if -1 in end_set:
            end_set.remove(-1)

        end = len(text)
        if end_set:
            end = min(end_set)

        candidate_answer = text[:end].strip()
        candidate_answer = re.sub(r"(.*)<\|.*\|>", r"\1", candidate_answer).strip()

        if str(prompt.to_dict()) not in self._cache:
            self._cache[str(prompt.to_dict())] = candidate_answer

        if not candidate_answer:
            candidate_answer = "unknown"

        return candidate_answer
