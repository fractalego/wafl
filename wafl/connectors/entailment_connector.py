from typing import Dict

import aiohttp
import asyncio
import json

from wafl.config import Configuration


class EntailmentConnector:
    _max_tries = 3

    def __init__(self, config=None):
        if not config:
            config = Configuration.load_local_config()

        self._server_url = (
            f"https://{config.get_value('model_host')}:"
            f"{config.get_value('model_port')}/predictions/entailment"
        )
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running Entailment Model.")

    async def predict(self, premise: str, hypothesis: str) -> Dict[str, float]:
        payload = {"premise": premise, "hypothesis": hypothesis}
        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(verify_ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    data = await response.text()
                    prediction = json.loads(data)
                    label_names = ["entailment", "neutral", "contradiction"]
                    return {
                        name: float(pred) for pred, name in zip(prediction, label_names)
                    }

        return "UNKNOWN"

    async def check_connection(self):
        payload = {"premise": "hello", "hypothesis": "a greeting"}
        try:
            async with aiohttp.ClientSession(
                conn_timeout=3, connector=aiohttp.TCPConnector(verify_ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    await response.text()
                    return True

        except aiohttp.client.InvalidURL:
            print()
            print("Is the entailment server running?")
            print("Please run 'bash start-llm.sh' (see docs for explanation).")
            print()

        return False
