import os
import json
import random

_path = os.path.dirname(__file__)
_samsum_train_path = os.path.join(_path, "data/samsum-train.json")
_squad_train_path = os.path.join(_path, "data/squad2-train.json")
_candidate_answers = [
    "unknown",
    "I don't know",
    "I do not know",
    "I have no information about this",
]
_unknown_fraction = 0.1


def get_speakers(dialogue):
    speakers = set()
    for line in dialogue.split("\n"):
        name = line[: line.find(":")]
        speakers.add(name)

    return list(speakers)


def select_random_pair_of_speakers(candidates):
    random.shuffle(candidates)
    return candidates[:2]


def create_inset_from_unanswerable_question(squad_set, first_speaker, second_speaker):
    data = squad_set["data"]
    item = random.choice(data)
    paragraph = random.choice(item["paragraphs"])
    qas = random.choice(paragraph["qas"])
    question = qas["question"]
    answer = random.choice(_candidate_answers)
    return f"{first_speaker}: {question}\n{second_speaker}: {answer}\n"


if __name__ == "__main__":
    samsum_train = json.load(open(_samsum_train_path))
    squad_train = json.load(open(_squad_train_path))

    new_train_set = []
    for item in samsum_train:
        new_item = {}

        dialogue = item["dialogue"]
        if not dialogue:
            continue

        speakers = get_speakers(dialogue)
        first, second = select_random_pair_of_speakers(speakers)
        inset = create_inset_from_unanswerable_question(squad_train, first, second)

        new_dialogue = ""
        num_lines = len(dialogue.split("\n"))
        inserted_before = False
        for line in dialogue.split("\n"):
            new_dialogue += line + "\n"
            threshold = _unknown_fraction / num_lines
            if random.uniform(0, 1) < threshold and not inserted_before:
                new_dialogue += inset
                inserted_before = True

        new_dialogue = "In the dialogue below some people are talking:\n" + new_dialogue
        new_item["dialogue"] = new_dialogue.replace("\r", "")
        new_train_set.append(new_item)

    json.dump(
        new_train_set[:1000], open(os.path.join(_path, "data/dialogues.json"), "w")
    )
