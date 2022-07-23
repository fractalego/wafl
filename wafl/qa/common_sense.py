import logging
import os
import torch

from transformers import GPT2LMHeadModel, GPT2Tokenizer
from wafl.qa.dataclasses import Answer
from wafl.qa.utils import get_answer_from_text, get_text_up_to_question

_path = os.path.dirname(__file__)
_logger = logging.getLogger(__file__)
_tokenizer = GPT2Tokenizer.from_pretrained("gpt2")
_model = GPT2LMHeadModel.from_pretrained("gpt2")
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
checkpoint = torch.load(
    os.path.join("/home/alce/src/wafl/models/save_creak5"), map_location=device
)
### CHANGE PATH (DOWNLOAD FROM REPO)
_model.load_state_dict(checkpoint["model_state_dict"])
_model = _model.to(device)


class CommonSense:
    def claim_makes_sense(self, claim):
        text = f"The claim is:\n{claim}\n\nThe claim makes sense:\n"
        if generate_answer(_model, text) == "Y":
            return Answer(text="True")

        return Answer(text="False")


def generate_answer(model, text):
    prompt = get_text_up_to_question(text)
    tokens = _tokenizer.encode(prompt, return_tensors="pt")
    _length = 70
    tokens_length = tokens.shape[1]
    if tokens_length + _length >= 1024:
        raise RuntimeError("Text is longer than 1024")
    output = model.generate(
        tokens.cuda(), max_length=tokens_length + _length, pad_token_id=50256
    )
    output = _tokenizer.decode(output[0], skip_special_tokens=True)
    return get_answer_from_text(output)
