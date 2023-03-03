import json
import requests
import transformers

from wafl.config import Configuration

_tokenizer = transformers.AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")


class BaseGPTJConnector:
    _max_tries = 3
    _max_reply_length = 50
    _num_prediction_tokens = 5

    def __init__(self, config=None):
        if not config:
            config = Configuration.load_local_config()

        self._server_url = (
            f"https://{config.get_value('model_host')}:"
            f"{config.get_value('model_port')}/predictions/bot"
        )
        if not self.check_connection():
            raise RuntimeError("Cannot connect a running Language Model.")

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

    def check_connection(self):
        try:
            payload = {"data": "test", "num_beams": 1, "num_tokens": 5}
            requests.post(self._server_url, json=payload, verify=False)
            return True

        except requests.ConnectionError as e:
            print(e)
            print()
            print("Is the wafl-llm running?")
            print("Please run 'bash start-llm.sh' (see docs for explanation).")
            print()
            return False

    def get_answer(self, text, dialogue, query):
        prompt = self._get_answer_prompt(text, query, dialogue)
        text = prompt
        start = text.rfind(":") + 1
        while (
            all(item not in text[start:] for item in ["\n", ". "])
            and len(text) < start + self._max_reply_length
        ):
            text += self.predict(text)

        end_set = set()
        end_set.add(text.find("\n", start))
        end_set.add(text.find(". ", start))
        if -1 in end_set:
            end_set.remove(-1)

        end = len(text)
        if end_set:
            end = min(end_set)

        candidate_answer = text[start:end].split(":")[-1].strip()
        return candidate_answer

    def _get_answer_prompt(self, text, query, dialogue=None):
        raise NotImplementedError("_get_answer_prompt() needs to be implemented.")
