import aiohttp
import asyncio

from wafl.connectors.base_llm_connector import BaseLLMConnector


class RemoteLLMConnector(BaseLLMConnector):
    _max_tries = 3
    _max_reply_length = 1024
    _num_prediction_tokens = 200
    _cache = {}
    _num_replicas = 10

    def __init__(self, config, last_strings=None):
        super().__init__(last_strings)
        host = config["model_host"]
        port = config["model_port"]
        self._server_url = f"https://{host}:{port}/predictions/bot"

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running LLM.")

    async def predict(self, prompt: str, temperature=None, num_tokens=None) -> [str]:
        if not temperature:
            temperature = 0.5

        if not num_tokens:
            num_tokens = self._num_prediction_tokens

        payload = {
            "data": prompt,
            "temperature": temperature,
            "num_tokens": num_tokens,
            "last_strings": self._last_strings,
            "num_replicas": self._num_replicas,
        }

        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    answer = await response.text()
                    return answer.split("<||>")

        return [""]

    async def check_connection(self):
        payload = {
            "data": "test",
            "temperature": 0.6,
            "num_tokens": 1,
            "last_strings": self._last_strings,
            "num_replicas": self._num_replicas,
        }
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
