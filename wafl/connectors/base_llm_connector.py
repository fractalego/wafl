import aiohttp
import asyncio
import re

from wafl.config import Configuration


class BaseLLMConnector:
    _max_tries = 3
    _max_reply_length = 150
    _num_prediction_tokens = 10

    def __init__(self, config=None):
        if not config:
            config = Configuration.load_local_config()

        self._server_url = (
            f"https://{config.get_value('model_host')}:"
            f"{config.get_value('model_port')}/predictions/bot"
        )

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running GPT-J Model.")

        self._cache = {}

    async def predict(self, prompt: str) -> str:
        payload = {
            "data": prompt,
            "num_beams": 1,
            "num_tokens": self._num_prediction_tokens,
        }

        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    answer = await response.text()
                    if not answer:
                        answer = "<|END|>"

                    return answer

        return "UNKNOWN"

    async def check_connection(self):
        payload = {"data": "test", "num_beams": 1, "num_tokens": 5}
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

    async def get_answer(self, text: str, dialogue: str, query: str) -> str:
        prompt = await self._get_answer_prompt(text, query, dialogue)
        if prompt in self._cache:
            return self._cache[prompt]

        text = prompt
        start = len(text)
        while (
            all(item not in text[start:] for item in [". ", "<|END|>", "user:"])
            and len(text) < start + self._max_reply_length
        ):
            text += await self.predict(text)

        end_set = set()
        end_set.add(text.find(". ", start))
        end_set.add(text.find("user:", start))
        end_set.add(text.find("<|END|>", start))
        if -1 in end_set:
            end_set.remove(-1)

        end = len(text)
        if end_set:
            end = min(end_set)

        candidate_answer = text[start:end].split("bot: ")[-1].strip()
        candidate_answer = re.sub(r"\[.*](.*)", r"\1", candidate_answer).strip()
        candidate_answer = re.sub(r"(.*)<\|.*\|>", r"\1", candidate_answer).strip()

        if prompt not in self._cache:
            self._cache[prompt] = candidate_answer

        return candidate_answer

    async def _get_answer_prompt(self, text, query, dialogue=None):
        raise NotImplementedError("_get_answer_prompt() needs to be implemented.")
