import torch


def get_answer_from_text(text):
    _claim_yn = "The claim makes sense:\n"
    pos = text.find(_claim_yn) + len(_claim_yn)
    return text[pos]


def get_text_up_to_question(text):
    _claim_yn = "The claim makes sense:\n"
    return text[: text.find(_claim_yn) + len(_claim_yn)]


def generate_answer_greedy(model, tokenizer, prompt, max_length=50):
    tokens = tokenizer.encode(prompt, return_tensors="pt")
    tokens_length = tokens.shape[1]
    if tokens_length + max_length > 1024:
        return ""

    while tokens.shape[-1] < tokens_length + max_length:
        new_tokens = model(tokens.cuda())
        pred_ids = torch.argmax(new_tokens.logits, dim=-1)
        last_token = pred_ids[:, -1].cpu().detach()
        tokens = torch.cat([tokens, torch.tensor([[last_token]])], dim=-1)
        last_output = tokenizer.decode(last_token, skip_special_tokens=True)
        if last_output == "\n":
            break

    generated_output = tokens[:, tokens_length:]
    output = tokenizer.decode(generated_output[0], skip_special_tokens=True)
    end = output.find("\n")
    return output[:end].replace("A: ", "").strip()


def create_prompt_for_qa(text, query, dialogue=None):
    text = text.strip()
    query = query.strip()

    prompt = "In the text below two people are discussing a story.\n\n"
    prompt += "Story:\n" + text + "\n\n"
    prompt += "Discussion:\n"
    if dialogue:
        dialogue = dialogue.strip()
        prompt += dialogue + "\n"
    prompt += "Q: " + query + "\n"
    return prompt
