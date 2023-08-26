import base64
import aiohttp
import asyncio
import json

from typing import Dict


class RemoteSpeakerConnector:
    _max_tries = 3

    def __init__(self, config):
        self._server_url = (
            f"https://{config['model_host']}:"
            f"{config['model_port']}/predictions/speaker"
        )
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running Speaker Model.")

    async def predict(self, text: str) -> Dict[str, float]:
        payload = {"text": text}
        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    data = await response.text()
                    prediction = json.loads(data)
                    wav = prediction["wav"]
                    rate = prediction["rate"]
                    return {"wav": base64.b64decode(wav), "rate": rate}

        return {"wav": "", "rate": 16000}

    async def check_connection(self):
        payload = {"text": "test"}
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
