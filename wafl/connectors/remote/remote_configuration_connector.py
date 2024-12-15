import aiohttp
import asyncio
import json

from typing import Dict
from wafl.variables import get_variables


class RemoteConfigurationConnector:
    _max_tries = 3

    def __init__(self, host: str, port: int):
        self._server_url = f"https://{host}:{port}/predictions/configuration"
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError(
                "Cannot connect a running Configuration handler. Is WAFL-LLM running?"
            )

    async def predict(self) -> Dict[str, str]:
        payload = {"version": get_variables()["version"]}
        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    data = await response.text()
                    prediction = json.loads(data)
                    listener_model = prediction["listener_model"]
                    speaker_model = prediction["speaker_model"]
                    text_embedding_model = prediction["text_embedding_model"]
                    entailer_model = prediction["entailer_model"]
                    llm_model = prediction["llm_model"]
                    return {
                        "listener_model": listener_model,
                        "speaker_model": speaker_model,
                        "text_embedding_model": text_embedding_model,
                        "entailer_model": entailer_model,
                        "llm_model": llm_model,
                    }

        return {}

    async def check_connection(self) -> bool:
        try:
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                payload = {"version": get_variables()["version"]}
                async with session.post(self._server_url, json=payload) as response:
                    return response.status == 200

        except Exception:
            return False
