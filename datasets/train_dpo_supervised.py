import os

import pandas as pd
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
from svd_training.svd_model import SVDMistralForCausalLM

model_name = "mistralai/Mistral-7B-Instruct-v0.1"
tokenizer = AutoTokenizer.from_pretrained(model_name)
tokenizer.pad_token = tokenizer.eos_token
_filename = "mistral_svd_model.psd"
if os.path.exists(_filename):
    model = SVDMistralForCausalLM.create_from_state_dict(torch.load(_filename))

else:
    model = SVDMistralForCausalLM.create_from_model(AutoModelForCausalLM.from_pretrained(model_name),
                                                    rank_fraction=0.1)
    torch.save(model.state_dict(), _filename)


def normalize_conversations(text):
    # text = text.replace("\nuser: ", "<|endoftext|>\n<|user|>\n")
    # text = text.replace("user: ", "<|user|>\n")
    # text = text.replace("\nbot: ", "<|endoftext|>\n<|assistant|>\n")
    # text = text + "<|endoftext|>"
    return text


def normalize_prompt(text):
    # text = "<|system|>\n" + text
    return text


def create_train_dataset(df):
    prompts = []
    chosen = []
    rejected = []
    for _, row in df.iterrows():
        prompts.append(normalize_prompt("This is the summary of the bot's knowledge: \n" + row["memory"].strip() \
                                        + "\n\nThe rules are as follows:\n" + row[
                                            "rules"].strip() + "\n\nThe conversation goes as follows:\n"))
        chosen.append(normalize_conversations(row["positive_conversation"]))
        rejected.append(normalize_conversations(row["negative_conversation"]))

    return Dataset.from_dict({"prompt": prompts, "chosen": chosen, "rejected": rejected})


def my_loss(logits, original_logits, target):
    loss = torch.mean((output - target)**2)


    return loss



if __name__ == '__main__':
    df = pd.read_parquet("data/wafl_functions.parquet")
    train_dataset = create_train_dataset(df)
    sample_text = train_dataset[0]["prompt"] + train_dataset[0]["chosen"]
    optimizer = torch.optim.Adam(model.parameters(), lr=1e-5)
    input_ids = tokenizer(sample_text, return_tensors="pt").input_ids
    output = model(input_ids)
    loss = output.loss
    loss.backward()
    optimizer.step()
    print("Done")

    input_ids = tokenizer(train_dataset[1]["prompt"], return_tensors="pt").input_ids
    output = model.generate(input_ids, max_length=input_ids.shape[1] + 2, use_cache=True)
    print(tokenizer.decode(output[0], skip_special_tokens=True))

