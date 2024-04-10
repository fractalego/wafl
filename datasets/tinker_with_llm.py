import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM

tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-Instruct-v0.1")
model = AutoModelForCausalLM.from_pretrained("./wafl_functions")


def create_train_dataset(df):
    prompts = []
    chosen = []
    rejected = []
    for _, row in df.iterrows():
        prompts.append("This is the summary of the bot's knowledge: \n" + row["memory"].strip() \
                       + "\n\nThe rules are as follows:\n" + row[
                           "rules"].strip() + "\n\nThe conversation goes as follows:\n")
        chosen.append(row["positive_conversation"].strip())
        rejected.append(row["negative_conversation"].strip())

    return Dataset.from_dict({"prompt": prompts, "chosen": chosen, "rejected": rejected})


if __name__ == '__main__':
    df = pd.read_parquet("data/wafl_functions.parquet")
    train_dataset = create_train_dataset(df)
    user_string = "\nuser: write a haiku about cherry blossom.\nbot:"
    input_ids = tokenizer(train_dataset[0]["prompt"] + user_string, return_tensors="pt")
    #outputs = model.generate(**input_ids, max_length=input_ids.input_ids.shape[1] + 2, use_cache=True)
    outputs = model.generate(**input_ids, do_sample=True, temperature=0.4, max_length=1024,
                             pad_token_id=tokenizer.eos_token_id)
    print(tokenizer.decode(outputs[0]))
