import json
import requests
import transformers

from wafl.config import Configuration

_tokenizer = transformers.AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")


class BaseGPTJConnector:
    _max_tries = 3
    _max_reply_length = 100
    _num_prediction_tokens = 5

    def __init__(self, config=None):
        if not config:
            config = Configuration.load_local_config()

        self._server_url = (
            f"https://{config.get_value('model_host')}:"
            f"{config.get_value('model_port')}/predictions/bot"
        )
        self._check_connection()

    def predict(self, prompt: str) -> str:
        payload = {"data": prompt, "num_beams": 1, "num_tokens": 5}
        for _ in range(self._max_tries):
            try:
                r = requests.post(self._server_url, json=payload, verify=False)
                answer = json.loads(r.content.decode("utf-8"))
                return _tokenizer.decode(answer[-self._num_prediction_tokens])

            except requests.exceptions.ConnectionError:
                continue

        return "UNKNOWN"

    def _check_connection(self):
        try:
            payload = {"data": "test", "num_beams": 1, "num_tokens": 5}
            r = requests.post(self._server_url, json=payload, verify=False)

        except requests.ConnectionError as e:
            print(e)
            print()
            print("Is the wafl-llm running?")
            print("Please run 'bash start-llm.sh' (see docs for explanation).")
            print()
