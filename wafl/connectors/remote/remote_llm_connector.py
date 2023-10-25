import aiohttp
import asyncio
import time
import re


class RemoteLLMConnector:
    _max_tries = 3
    _max_reply_length = 1024
    _num_prediction_tokens = 200
    _cache = {}

    def __init__(self, config):
        host = config["remote_model"]["model_host"]
        port = config["remote_model"]["model_port"]
        self._server_url = f"https://{host}:{port}/predictions/bot"

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running LLM.")

    async def predict(self, prompt: str) -> str:
        payload = {
            "data": prompt,
            "temperature": 0.5,
            "num_tokens": self._num_prediction_tokens,
            "last_strings": ["\nuser:", "\nbot:"],
        }

        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    answer = await response.text()
                    if not answer:
                        answer = "<|EOS|>"

                    return answer

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
            all(
                item not in text[start:]
                for item in ["\nuser:", "\nbot:", "<|EOS|>"]
            )
            and len(text) < start + self._max_reply_length
        ):
            text += await self.predict(text)

        end_set = set()
        end_set.add(text.find("\nuser:", start))
        end_set.add(text.find("\nbot:", start))
        end_set.add(text.find("\n<|EOS|>:", start))
        if -1 in end_set:
            end_set.remove(-1)

        end = len(text)
        if end_set:
            end = min(end_set)

        candidate_answer = text[start:end].split("bot: ")[-1].strip()
        candidate_answer = re.sub(r"(.*)<\|.*\|>", r"\1", candidate_answer).strip()

        self._cache[prompt] = candidate_answer

        print(time.time() - start_time)
        if not candidate_answer:
            candidate_answer = "unknown"

        return candidate_answer

    async def check_connection(self):
        payload = {"data": "test", "temperature": 0.5, "num_tokens": 1}
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
