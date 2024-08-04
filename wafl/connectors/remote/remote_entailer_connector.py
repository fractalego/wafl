import aiohttp
import asyncio
import json
import numpy as np

from typing import Dict, List


class RemoteEntailerConnector:
    _max_tries = 3

    def __init__(self, config):
        host = config["model_host"]
        port = config["model_port"]

        self._server_url = f"https://{host}:" f"{port}/predictions/entailer"
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running Entailment Model.")

    async def predict(self, lhs: str, rhs: str) -> Dict[str, float]:
        payload = {"lhs": lhs, "rhs": rhs}
        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    data = await response.text()
                    prediction = json.loads(data)
                    score = prediction["score"]
                    return {"score": float(score)}

        return {"score": -1.0}

    async def check_connection(self):
        payload = {"lhs": "test", "rhs": "test"}
        try:
            async with aiohttp.ClientSession(
                conn_timeout=3, connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    await response.text()
                    return True

        except aiohttp.client.InvalidURL:
            print()
            print("Is the entailer server running?")
            print("Please run 'bash start-llm.sh' (see docs for explanation).")
            print()

        return False
