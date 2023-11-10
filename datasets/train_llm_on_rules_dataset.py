import random

import pandas as pd
from datasets import Dataset
from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer, DataCollatorForLanguageModeling

model_name_or_path = 'mistralai/Mistral-7B-Instruct-v0.1'
max_length = 1024 + 512

def get_prompts(df):
    prompts = []
    for _, row in df.sample(frac=1).iterrows():
        memory = ""
        if memory == "":
            memory = "The user has no memory."

        current_rule = row["Rules"]
        rules = df.sample(random.choice([1, 2]))["Rules"].tolist() + [current_rule]
        random.shuffle(rules)
        rules = "\n".join(rules)
        prompt = f"""
The user is talking with a chatbot about the theme \"{row["Theme"]}\" based on the following summary.
<summary>
{memory}
</summary>

The rules are as follows:
<rules>
{rules}
</rules>

The conversation goes as follows:
{row["Conversation"]}
        """.strip() + "\n\n"
        prompts.append(prompt)

    return prompts


def preprocess_function(sample):
    model_inputs = tokenizer(sample["prompt"],
                             return_tensors="pt",
                             max_length=max_length,
                             padding='max_length')
    labels = tokenizer(sample["prompt"],
                       return_tensors="pt",
                       max_length=max_length,
                       padding='max_length')

    model_inputs["labels"] = labels["input_ids"]
    return model_inputs


def model_init():
    model = AutoModelForCausalLM.from_pretrained(model_name_or_path)
    parameters = model.parameters()
    for parameter in parameters:
        parameter.requires_grad = False

    model.model.enable_input_require_grads()
    model.lm_head.training = True
    for index in range(len(model.model.layers)):
        model.model.layers[index].self_attn.k_proj.training = True

    return model


def create_dataset_from_file(filepath):
    df = pd.read_csv(filepath)
    prompts = get_prompts(df)
    return Dataset.from_dict({"prompt": prompts})


if __name__ == '__main__':
    tokenizer = AutoTokenizer.from_pretrained(model_name_or_path)
    tokenizer.pad_token = tokenizer.eos_token
    dataset = create_dataset_from_file("data/complex_instructions.csv")
    train_dataset = dataset.map(preprocess_function, batched=True, batch_size=1, num_proc=4)
    data_collator = DataCollatorForLanguageModeling(tokenizer, mlm=False)
    learning_rate = 1e-6
    output_dir_name = f"checkpoint_lr{learning_rate}"
    training_args = TrainingArguments(
        output_dir=output_dir_name,
        per_device_train_batch_size=1,
        per_device_eval_batch_size=1,
        evaluation_strategy="steps",
        use_cpu=True,
        learning_rate=learning_rate,
        num_train_epochs=2,
        logging_steps=200,
        eval_steps=200,
        save_total_limit=1,
    )
    model = model_init()
    trainer = Trainer(
        model=model,
        args=training_args,
        tokenizer=tokenizer,
        data_collator=data_collator,
        train_dataset=train_dataset,
    )
    trainer.train()
    trainer.save_model("wafl-mistral")
    model = trainer.model
    model.push_to_hub("fractalego/wafl-mistral")
    tokenizer.push_to_hub("fractalego/wafl-mistral")
