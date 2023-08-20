import aiohttp
import asyncio
import json
import numpy as np

from typing import Dict, List


class RemoteSentenceEmbedderConnector:
    _max_tries = 3

    def __init__(self, config):
        host = config["remote_model"]["model_host"]
        port = config["remote_model"]["model_port"]
        model_name = config["local_model"]

        self._model_name = model_name
        self._server_url = f"https://{host}:" f"{port}/predictions/sentence_embedder"
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running Entailment Model.")

    async def predict(self, text: str) -> Dict[str, List[float]]:
        payload = {"text": text, "model_name": self._model_name}
        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    data = await response.text()
                    prediction = json.loads(data)
                    embedding = prediction["embedding"]
                    return {"embedding": np.array(embedding)}

        return {"embedding": [0.0]}

    async def check_connection(self):
        payload = {"text": "test", "model_name": "model_name"}
        try:
            async with aiohttp.ClientSession(
                conn_timeout=3, connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    await response.text()
                    return True

        except aiohttp.client.InvalidURL:
            print()
            print("Is the whisper server running?")
            print("Please run 'bash start-llm.sh' (see docs for explanation).")
            print()

        return False
