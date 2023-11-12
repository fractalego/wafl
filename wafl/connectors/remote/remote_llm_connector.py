import aiohttp
import asyncio
import time
import re

from wafl.connectors.utils import select_best_answer


class RemoteLLMConnector:
    _max_tries = 3
    _max_reply_length = 1024
    _num_prediction_tokens = 200
    _cache = {}

    def __init__(self, config, last_strings=None):
        host = config["remote_model"]["model_host"]
        port = config["remote_model"]["model_port"]
        self._server_url = f"https://{host}:{port}/predictions/bot"
        if not last_strings:
            self._last_strings = ["\nuser:", "\nbot:", "<|EOS|>", "</remember>", "</execute>\n", "</execute>\n", "</s>"]

        else:
            self._last_strings = last_strings

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running LLM.")

    async def predict(self, prompt: str, temperature=None, num_tokens=None) -> str:
        if not temperature:
            temperature = 0.5

        if not num_tokens:
            num_tokens = self._num_prediction_tokens

        payload = {
            "data": prompt,
            "temperature": temperature,
            "num_tokens": num_tokens,
            "last_strings": self._last_strings,
            "num_replicas": 3,
        }

        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    answer = await response.text()
                    return select_best_answer(answer.split("<||>"))

        return "UNKNOWN"

    async def generate(self, prompt: str) -> str:
        print(__name__)
        start_time = time.time()
        if prompt in self._cache:
            print(time.time() - start_time)
            return self._cache[prompt]

        text = prompt
        start = len(text)
        while (
            all(item not in text[start:] for item in self._last_strings)
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

        candidate_answer = text[start:end].strip()
        candidate_answer = re.sub(r"(.*)<\|.*\|>", r"\1", candidate_answer).strip()

        self._cache[prompt] = candidate_answer

        print(time.time() - start_time)
        if not candidate_answer:
            candidate_answer = "unknown"

        return candidate_answer

    async def check_connection(self):
        payload = {"data": "test", "temperature": 0.6, "num_tokens": 1}
        try:
            async with aiohttp.ClientSession(
                conn_timeout=3, connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    await response.text()
                    return True

        except aiohttp.client.InvalidURL:
            print()
            print("Is the wafl-llm running?")
            print("Please run 'bash start-llm.sh' (see docs for explanation).")
            print()

        return False
