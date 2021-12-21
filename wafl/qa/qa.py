import logging
import os
import torch

from dataclasses import dataclass
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from fact_checking import FactChecker

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)
_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
_model = GPT2LMHeadModel.from_pretrained("gpt2")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
checkpoint = torch.load(
    os.path.join("/home/alce/src/wafl/models/save_small6"), map_location=device
)
### CHANGE PATH (DOWNLOAD FROM REPO)
_model.load_state_dict(checkpoint["model_state_dict"])
_model = _model.to(device)
_forbidden_words = set(
    [
        item.strip().lower()
        for item in open(
            os.path.join(_path, "/home/alce/src/wafl/data/bad-words.txt")
        ).readlines()
    ]
)
### CHANGE PATH (DOWNLOAD FROM REPO)
_fact_checking_model = GPT2LMHeadModel.from_pretrained("gpt2")
checkpoint = torch.load(
    os.path.join(_path, "/home/alce/src/wafl/models/save_fever0"), map_location=device
)
### CHANGE PATH (DOWNLOAD FROM REPO)
_fact_checking_model.load_state_dict(checkpoint["model_state_dict"])


@dataclass
class Query:
    text: str
    is_question: bool
    variable: str = None


@dataclass
class Answer:
    text: str
    variable: str = None


class QA:
    def __init__(self):
        self._fact_checker = FactChecker(_fact_checking_model, _tokenizer)

    def ask(self, query: "Query", text: str):
        if query.is_question:
            return self.__answer_question(query, text)

        return self.__check_fact(query, text)

    def __answer_question(self, query: "Query", text: str):
        answer, _ = _generate_answer(text, query.text)
        if answer.lower() == "unknown":
            return "False"

        return Answer(text=answer, variable=query.variable)

    def __check_fact(self, query, text):
        answer = self._fact_checker.validate(query.text, text)
        return Answer(text=str(answer))


def _generate_answer(text, query, dialogue=None, length=50):
    text = text.strip()
    query = query.strip()

    prompt = "In the text below two people are discussing a story.\n\n"
    prompt += "Story:\n" + text + "\n\n"
    prompt += "Discussion:\n"
    if dialogue:
        dialogue = dialogue.strip()
        prompt += dialogue + "\n"
    prompt += "Q: " + query + "\n"
    tokens = _tokenizer.encode(prompt, return_tensors="pt")
    tokens_length = tokens.shape[1]
    out_tokens = _model.generate(
        tokens.to(device),
        max_length=tokens_length + length,
        temperature=0,
        pad_token_id=50256,
    )
    generated_text = _tokenizer.decode(
        out_tokens[:, tokens_length:][0], skip_special_tokens=True
    )
    score = float(_model(out_tokens, labels=out_tokens)[0])
    start = 0
    end = generated_text.find("\n", start + 1)
    if end == -1:
        end = len(generated_text)
    answer = generated_text[start : end + 1].split("A:")[-1].strip()
    if len(set(answer.split()) & _forbidden_words) > 0:
        _logger.warning("A forbidden word was caught in the answer!")
        answer = "unknown"
    return answer, score
