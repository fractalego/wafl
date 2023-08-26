import aiohttp
import asyncio
import json

from typing import Dict


class RemoteEntailmentConnector:
    _max_tries = 3

    def __init__(self, config):
        self._server_url = (
            f"https://{config['remote_model']['model_host']}:"
            f"{config['remote_model']['model_port']}/predictions/entailment"
        )
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running Entailment Model.")

        self._cache = {}

    async def predict(self, premise: str, hypothesis: str) -> Dict[str, float]:
        if (premise, hypothesis) in self._cache:
            return self._cache[(premise, hypothesis)]

        payload = {"premise": premise, "hypothesis": hypothesis}
        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    data = await response.text()
                    prediction = json.loads(data)
                    label_names = ["entailment", "neutral", "contradiction"]
                    answer = {
                        name: float(pred) for pred, name in zip(prediction, label_names)
                    }
                    if (premise, hypothesis) not in self._cache:
                        self._cache[(premise, hypothesis)] = answer

                    return answer

        return "UNKNOWN"

    async def check_connection(self):
        payload = {"premise": "hello", "hypothesis": "a greeting"}
        try:
            async with aiohttp.ClientSession(
                conn_timeout=3, connector=aiohttp.TCPConnector(ssl=False)
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
