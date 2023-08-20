import aiohttp
import asyncio
import json

from typing import Dict


class RemoteWhisperConnector:
    _max_tries = 3

    def __init__(self, config):
        self._server_url = (
            f"https://{config['model_host']}:"
            f"{config['model_port']}/predictions/whisper"
        )
        try:
            loop = asyncio.get_running_loop()

        except RuntimeError:
            loop = None

        if (not loop or (loop and not loop.is_running())) and not asyncio.run(
            self.check_connection()
        ):
            raise RuntimeError("Cannot connect a running Whisper remote model.")

    async def predict(self, waveform, hotword=None) -> Dict[str, float]:
        payload = {
            "waveform": waveform.tolist(),
            "num_beams": 3,
            "num_tokens": 15,
            "hotword": hotword,
        }
        for _ in range(self._max_tries):
            async with aiohttp.ClientSession(
                connector=aiohttp.TCPConnector(ssl=False)
            ) as session:
                async with session.post(self._server_url, json=payload) as response:
                    data = await response.text()
                    prediction = json.loads(data)
                    transcription = prediction["transcription"]
                    score = prediction["score"]
                    logp = prediction["logp"]
                    return {
                        "transcription": transcription,
                        "score": score,
                        "logp": logp,
                    }

        return {"transcription": "", "score": 0.0}

    async def check_connection(self):
        payload = {"waveform": [0], "num_beams": 3, "num_tokens": 15}
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
