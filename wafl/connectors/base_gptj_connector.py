import aiohttp
import asyncio
import json
import re
import transformers

from wafl.config import Configuration

_tokenizer = transformers.AutoTokenizer.from_pretrained(
    "EleutherAI/gpt-neo-2.7B", padding_side="left"
)


class BaseGPTJConnector:
    _max_tries = 3
    _max_reply_length = 70
    _num_prediction_tokens = 5

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

    async def predict(self, prompt: str) -> str:
        payload = {"data": prompt, "num_beams": 1, "num_tokens": 5}
        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    data = await response.text()
                    answer = json.loads(data)
                    answer = [item for item in answer if item > 0]
                    return _tokenizer.decode(answer[-self._num_prediction_tokens :])

        return "UNKNOWN"

    async def check_connection(self):
        payload = {"data": "test", "num_beams": 1, "num_tokens": 5}
        try:
            async with aiohttp.ClientSession(
                conn_timeout=3, connector=aiohttp.TCPConnector(verify_ssl=False)
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
        prompt = self._get_answer_prompt(text, query, dialogue)
        text = prompt
        start = len(text)
        while (
            all(item not in text[start:] for item in ["\n", ". "])
            and len(text) < start + self._max_reply_length
        ):
            text += await self.predict(text)

        end_set = set()
        end_set.add(text.find("\n", start))
        end_set.add(text.find(". ", start))
        if -1 in end_set:
            end_set.remove(-1)

        end = len(text)
        if end_set:
            end = min(end_set)

        candidate_answer = text[start:end].split(":")[-1].strip()
        candidate_answer = re.sub(r"\[.*](.*)", r"\1", candidate_answer).strip()
        return candidate_answer

    def _get_answer_prompt(self, text, query, dialogue=None):
        raise NotImplementedError("_get_answer_prompt() needs to be implemented.")
