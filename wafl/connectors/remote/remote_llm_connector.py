import json

import aiohttp
import asyncio

from wafl.connectors.base_llm_connector import BaseLLMConnector
from wafl.connectors.prompt_template import PromptTemplate
from wafl.variables import is_supported


class RemoteLLMConnector(BaseLLMConnector):
    _max_tries = 3
    _max_reply_length = 1024
    _num_prediction_tokens = 200
    _cache = {}

    def __init__(self, config, last_strings=None, num_replicas=1):
        super().__init__(last_strings)
        host = config["model_host"]
        port = config["model_port"]
        self._default_temperature = config["temperature"]
        self._server_url = f"https://{host}:{port}/predictions/bot"
        self._num_replicas = num_replicas

        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running LLM.")

    async def predict(
        self,
        prompt: PromptTemplate,
        temperature=None,
        num_tokens=None,
        num_replicas=None,
    ) -> [str]:
        if not temperature:
            temperature = self._default_temperature

        if not num_tokens:
            num_tokens = self._num_prediction_tokens

        if not num_replicas:
            num_replicas = self._num_replicas

        payload = {
            "data": prompt.to_dict(),
            "temperature": temperature,
            "num_tokens": num_tokens,
            "num_replicas": num_replicas,
        }

        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                conn_timeout=6000,
                connector=aiohttp.TCPConnector(ssl=False),
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    answer = json.loads(await response.text())
                    status = answer["status"]
                    if status != "success":
                        raise RuntimeError(f"Error in prediction: {answer}")
                    return answer["prediction"].split("<||>")

        return [""]

    async def check_connection(self):
        payload = {
            "data": {
                "system_prompt": "Hello!",
                "conversation": [{"speaker": "user", "text": "Hi!"}],
            },
            "temperature": 0.6,
            "num_tokens": 1,
            "last_strings": self._important_strings,
            "num_replicas": self._num_replicas,
        }
        try:
            async with aiohttp.ClientSession(
                conn_timeout=3, connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    answer = json.loads(await response.text())
                    wafl_llm_version = answer["version"]
                    print(f"Connected to wafl-llm v{wafl_llm_version}.")
                    if not is_supported(wafl_llm_version):
                        print("This version of wafl-llm is not supported.")
                        print("Please update wafl-llm.")
                        raise aiohttp.client.InvalidURL

                    return True

        except aiohttp.client.InvalidURL:
            print()
            print("Is the wafl-llm running?")
            print("Please run 'bash start-llm.sh' (see docs for explanation).")
            print()

        return False
