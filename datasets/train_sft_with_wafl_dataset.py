import os

import pandas as pd
import torch
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments
from svd_training.svd_model import SVDMistralForCausalLM
from trl import DPOTrainer, SFTTrainer

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
    texts = []
    for _, row in df.iterrows():
        texts.append(normalize_prompt("This is the summary of the bot's knowledge: \n" + row["memory"].strip() \
                                      + "\n\nThe rules are as follows:\n" + row[
                                          "rules"].strip() + "\n\nThe conversation goes as follows:\n")
                     + normalize_conversations(row["positive_conversation"])
                     )

    return Dataset.from_dict({"text": texts})


if __name__ == '__main__':
    df = pd.read_parquet("data/wafl_functions.parquet")
    train_dataset = create_train_dataset(df)
    training_args = TrainingArguments(output_dir="./output",
                                      #fp16_full_eval=True,
                                      use_cpu=True,
                                      num_train_epochs=0.001,
                                      gradient_checkpointing=True,
                                      per_device_train_batch_size=1,
                                      learning_rate=1e-7,
                                      save_strategy="steps",
                                      logging_steps=10,
                                      )
    trainer = SFTTrainer(
        model,
        train_dataset=train_dataset,
        dataset_text_field="text",
        tokenizer=tokenizer,
        max_seq_length=512,
        args=training_args,
    )
    trainer.train()
    model.merge_all()
    # input_ids = tokenizer("The capital of England is", return_tensors="pt").input_ids
    # output = model.generate(input_ids.cuda(), max_length=input_ids.shape[1] + 10, use_cache=True)
    # print(tokenizer.decode(output[0], skip_special_tokens=True))
    model.save_pretrained("wafl_functions")

#### SFT does not have -int
#### DPO introduces -inf after one step with 1e-8
#### Does SFTTrainer have a similar issue? If so, it is likely a problem with the Trainer class

#### TRY WIL LONGER CONTEXT WINDOW: DEFAULT IS 512 (LOOK FOR RIGHT ARGUMENT NAMES, THERE ARE TWO AT LEAST)
