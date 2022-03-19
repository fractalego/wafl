import logging
import os
import torch

from dataclasses import dataclass
from transformers import GPT2LMHeadModel, GPT2Tokenizer

from fact_checking import FactChecker

from wafl.qa.utils import generate_answer_greedy, create_prompt_for_qa

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
        query_text = query.text.strip()
        if query_text[-1] != "?":
            query_text += "?"

        answer = _generate_answer(text, query_text)

        return Answer(text=answer, variable=query.variable)

    def __check_fact(self, query, text):
        answer = self._fact_checker.validate(query.text, text)
        return Answer(text=str(answer))


def _generate_answer(text, query, dialogue=None, length=50):
    prompt = create_prompt_for_qa(text, query, dialogue)
    generated_text = generate_answer_greedy(_model, _tokenizer, prompt, length)
    if len(generated_text) > length:
        _logger.warning("The bot is hallucinating an answer. Resetting to unknown")
        return "unknown"

    answer = generated_text
    if len(set(answer.split()) & _forbidden_words) > 0:
        _logger.warning("A forbidden word was caught in the answer!")
        answer = "unknown"

    if answer and answer[-1] == ".":
        answer = answer[:-1]

    return answer


def get_perplexity(text):
    tokens = _tokenizer.encode(text, return_tensors="pt")
    return float(_model(tokens.to(device), labels=tokens.to(device))[0])
