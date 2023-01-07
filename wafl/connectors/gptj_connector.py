import json
import requests
import transformers

from wafl.config import Configuration

_tokenizer = transformers.AutoTokenizer.from_pretrained("EleutherAI/gpt-j-6B")


class GPTJConnector:
    _max_reply_length = 100

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
        r = requests.post(self._server_url, json=payload, verify=False)
        answer = json.loads(r.content.decode("utf-8"))
        return _tokenizer.decode(answer)

    def get_answer(self, text, dialogue, query):
        prompt = self._get_answer_prompt(text, query, dialogue)
        text = prompt
        start = len(prompt) - 1
        while (
            all(item not in text[start:] for item in ["\n", "."])
            and len(text) < start + self._max_reply_length
        ):
            output = self.predict(text)
            text += output[len(text) - 1 :]

        end = max(text.find("\n", start), text.find(".", start))
        return text[start:end].split(":")[-1].strip()

    def _get_answer_prompt(self, text, query, dialogue=None):
        text = text.strip()
        text = text.replace("\\'", "'")
        query = query.strip()

        prompt = "In the text below two people are discussing a story.\n\n"
        prompt += "Story:\n" + text + "\n\n"
        prompt += "Discussion:\n"
        if dialogue:
            dialogue = dialogue.strip()
            prompt += dialogue + "\n"

        prompt += "Q: " + query + "\n"
        prompt += "A:"
        return prompt

    def _check_connection(self):
        payload = {"data": "test", "num_beams": 1, "num_tokens": 5}
        r = requests.post(self._server_url, json=payload, verify=False)


class Dialogue:
    def __init__(self):
        self._dialogue_pairs = []

    def add_dialogue_pair(self, query: str, answer: str) -> "Dialogue":
        self._dialogue_pairs.append((query, answer))
        return self

    def get_text(self) -> str:
        text = ""
        for query, answer in self._dialogue_pairs:
            text += f"Q: {query}\n"
            text += f"A: {answer}\n"

        return text
