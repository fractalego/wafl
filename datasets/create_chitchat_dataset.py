import os
import json
import random
import re

from tqdm import tqdm


_path = os.path.dirname(__file__)
_samsum_train_path = os.path.join(_path, "data/samsum-train.json")
_squad_train_path = os.path.join(_path, "data/squad2-train.json")
_squad_filter_path = os.path.join(_path, "data/squad_items_about_people.json")
_candidate_answers = [
    "unknown",
    "I don't know",
    "I do not know",
    "I have no information about this",
]
_unknown_fraction = 0.1
_context_fraction = 0.2


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


def from_name_to_2nd_person(text, name):
    text = re.sub(f"{name} doesn't", "you don't", text, flags=re.IGNORECASE)
    text = re.sub(f"{name} does not", "you do not", text, flags=re.IGNORECASE)
    text = re.sub(f"{name} does", "you do", text, flags=re.IGNORECASE)
    text = re.sub(f"{name}'s", "your", text, flags=re.IGNORECASE)
    text = re.sub(f"does {name}", "do you", text, flags=re.IGNORECASE)
    text = re.sub(f"is {name}", "are you", text, flags=re.IGNORECASE)
    text = re.sub(f"was {name}", "were you", text, flags=re.IGNORECASE)
    text = re.sub(f"{name} is", "you are", text, flags=re.IGNORECASE)
    text = re.sub(f"{name}", "you", text, flags=re.IGNORECASE)
    return text


def from_name_to_1st_person(text, name):
    text = re.sub(f"{name} doesn't", "I don't", text, flags=re.IGNORECASE)
    text = re.sub(f"{name} does not", "I do not", text, flags=re.IGNORECASE)
    text = re.sub(f"{name} does", "I do", text, flags=re.IGNORECASE)
    text = re.sub(f"{name}'s", "my", text, flags=re.IGNORECASE)
    text = re.sub(f"does {name}", "do I", text, flags=re.IGNORECASE)
    text = re.sub(f"is {name}", "am I", text, flags=re.IGNORECASE)
    text = re.sub(f"was {name}", "was I", text, flags=re.IGNORECASE)
    text = re.sub(f"{name} is", "I am", text, flags=re.IGNORECASE)
    text = re.sub(f"to {name}", "to me", text, flags=re.IGNORECASE)
    text = re.sub(f"{name}", "I", text, flags=re.IGNORECASE)
    return text


def from_2nd_person_to_name(text, name):
    text = re.sub("you don't", f"{name} doesn't", text, flags=re.IGNORECASE)
    text = re.sub("you do not", f"{name} does not", text, flags=re.IGNORECASE)
    text = re.sub("you do", f"{name} does", text, flags=re.IGNORECASE)
    text = re.sub("your", f"{name}'s", text, flags=re.IGNORECASE)
    text = re.sub("do you", f"does {name}", text, flags=re.IGNORECASE)
    text = re.sub("are you", f"is {name}", text, flags=re.IGNORECASE)
    text = re.sub("were you", f"was {name}", text, flags=re.IGNORECASE)
    text = re.sub("you are", f"{name} is", text, flags=re.IGNORECASE)
    text = re.sub("you will", f"{name} will", text, flags=re.IGNORECASE)
    text = re.sub("you'll", f"{name} will", text, flags=re.IGNORECASE)
    text = re.sub(" you ", f" {name} ", text, flags=re.IGNORECASE)
    text = re.sub(" you\.", f" {name}\.", text, flags=re.IGNORECASE)
    text = re.sub(" you!", f" {name}!", text, flags=re.IGNORECASE)
    text = re.sub(" you\?", f" {name}\?", text, flags=re.IGNORECASE)
    return text


def from_1st_person_to_name(text, name):
    text = re.sub("I don't", f"{name} doesn't", text, flags=re.IGNORECASE)
    text = re.sub("I do not", f"{name} does not", text, flags=re.IGNORECASE)
    text = re.sub("I do", f"{name} does", text, flags=re.IGNORECASE)
    text = re.sub("my ", f"{name}'s ", text, flags=re.IGNORECASE)
    text = re.sub("do I", f"does {name}", text, flags=re.IGNORECASE)
    text = re.sub("am I", f"is {name}", text, flags=re.IGNORECASE)
    text = re.sub("was I", f"was {name}", text, flags=re.IGNORECASE)
    text = re.sub("I am", f"{name} is", text, flags=re.IGNORECASE)
    text = re.sub("to me", f"to {name}", text, flags=re.IGNORECASE)
    text = re.sub("I will", f"{name} will", text, flags=re.IGNORECASE)
    text = re.sub("I'll", f"{name} will", text, flags=re.IGNORECASE)
    text = re.sub("I'm", f"{name} is", text)
    text = re.sub("I ", f"{name} ", text)
    text = re.sub(" I\?", f" {name}\?", text)
    text = re.sub(" me ", f" {name} ", text, flags=re.IGNORECASE)
    text = re.sub(" me\.", f" {name}\.", text, flags=re.IGNORECASE)
    text = re.sub(" me!", f" {name}!", text, flags=re.IGNORECASE)
    text = re.sub(" me\?", f" {name}\?", text, flags=re.IGNORECASE)
    return text


def replace_names(text, names, replace_function):
    names = sorted(names, key=lambda x: -len(x))
    for name in names:
        if name in text:
            return replace_function(text, name)

    return text


def create_inset_with_first_person_answer(
    squad_set, squad_people_filter, first_speaker, second_speaker
):
    squad_item_number, names = random.sample(squad_people_filter.items(), 1)[0]
    squad_item_number = int(squad_item_number)
    names = names["names"]
    question, answer = "", ""
    while (
        "you" not in question.lower()
        and "your" not in question.lower()
        and "I " not in answer
        and "my" not in answer.lower()
    ):
        paragraph = random.choice(squad_set["data"][squad_item_number]["paragraphs"])
        qas = random.choice(paragraph["qas"])
        if not qas["answers"]:
            continue

        question = replace_names(qas["question"], names, from_name_to_2nd_person)
        answer = replace_names(
            random.choice(qas["answers"])["text"], names, from_name_to_1st_person
        )

    context = replace_names(
        paragraph["context"], names, lambda x, y: x.replace(y, second_speaker)
    )
    return f"{first_speaker}: {question}\n{second_speaker}: {answer}\n", context


def create_inset_with_first_person_query(
    squad_set, squad_people_filter, first_speaker, second_speaker
):
    squad_item_number, names = random.sample(squad_people_filter.items(), 1)[0]
    squad_item_number = int(squad_item_number)
    names = names["names"]
    question, answer = "", ""
    while (
        "I" not in question.lower()
        and "my" not in question.lower()
        and "you " not in answer.lower()
        and "your " not in answer.lower()
    ):
        paragraph = random.choice(squad_set["data"][squad_item_number]["paragraphs"])
        qas = random.choice(paragraph["qas"])
        if not qas["answers"]:
            continue

        question = replace_names(qas["question"], names, from_name_to_1st_person)
        answer = replace_names(
            random.choice(qas["answers"])["text"], names, from_name_to_2nd_person
        )

    context = replace_names(
        paragraph["context"], names, lambda x, y: x.replace(y, second_speaker)
    )
    return f"{first_speaker}: {question}\n{second_speaker}: {answer}\n", context


def is_question(line):
    return "?" in line


def get_sequence_of_speakers(dialogue_lines):
    return [line.split(":")[0] for line in dialogue_lines if ":" in line]


def find_next_speaker(speaker_sequence, index, curr_speaker):
    for speaker in speaker_sequence[index + 1 :]:
        if curr_speaker != speaker:
            return speaker

    raise RuntimeWarning("No next speaker in conversation.")


def find_prior_speaker(speaker_sequence, index, curr_speaker):
    for speaker in speaker_sequence[:index][::-1]:
        if curr_speaker != speaker:
            return speaker

    raise RuntimeError("No prior speaker in conversation.")


def substitute_pronouns_with_speaker_names(dialogue_text):
    dialogue_lines = [line for line in dialogue_text.split("\n") if line]
    speaker_sequence = get_sequence_of_speakers(dialogue_lines)
    new_lines = []
    for index in range(len(dialogue_lines) - 1):
        line = dialogue_lines[index]
        curr_speaker = speaker_sequence[index]
        if "remembers" in curr_speaker:
            new_lines.append(line)
            continue

        new_line = from_1st_person_to_name(line, curr_speaker)
        try:
            next_speaker = find_next_speaker(speaker_sequence, index, curr_speaker)

        except RuntimeWarning:
            new_lines.append(new_line)
            break

        new_line = from_2nd_person_to_name(new_line, next_speaker)
        new_lines.append(new_line)

    new_line = from_1st_person_to_name(dialogue_lines[-1], speaker_sequence[-1])
    try:
        prior_speaker = find_prior_speaker(speaker_sequence, -1, speaker_sequence[-1])

    except RuntimeWarning:
        new_lines.append(new_line)
        return "\n".join(new_lines)

    new_line = from_2nd_person_to_name(new_line, prior_speaker)
    new_lines.append(new_line)

    return "\n".join(new_lines)


if __name__ == "__main__":
    samsum_train = json.load(open(_samsum_train_path))
    squad_train = json.load(open(_squad_train_path))
    squad_people_filter = json.load(open(_squad_filter_path))

    new_train_set = []
    for item in tqdm(samsum_train[:1000]):
        new_item = {}
        dialogue = item["dialogue"].replace("\r", "")
        if not dialogue:
            continue

        speakers = get_speakers(dialogue)
        first, second = select_random_pair_of_speakers(speakers)
        inset = create_inset_from_unanswerable_question(squad_train, first, second)
        first_person_answer, sp_context = create_inset_with_first_person_answer(
            squad_train, squad_people_filter, first, second
        )
        first_person_query, fp_context = create_inset_with_first_person_query(
            squad_train, squad_people_filter, first, second
        )

        new_dialogue = ""
        num_lines = len(dialogue.split("\n"))
        unknown_inserted_before = False
        first_person_answer_inserted_before = False
        first_person_query_inserted_before = False

        for line in dialogue.split("\n"):
            new_dialogue += line + "\n"
            if line and is_question(line):
                continue

            threshold = _unknown_fraction / num_lines
            context_threshold = _context_fraction / num_lines
            if random.uniform(0, 1) < threshold and not unknown_inserted_before:
                new_dialogue += inset
                unknown_inserted_before = True

            elif (
                random.uniform(0, 1) < context_threshold
                and not first_person_answer_inserted_before
            ):
                if random.choice([1, 0]):
                    new_dialogue += f"{second} remembers: " + sp_context + "\n"
                    first_person_answer = first_person_answer.replace(
                        f"{second}:", f"{second}: [factual]"
                    )

                else:
                    new_dialogue += f"{second}: " + sp_context + "\n"
                    first_person_answer = first_person_answer.replace(
                        f"{second}:", f"{second}: [answer in conversation]"
                    )

                new_dialogue += first_person_answer
                first_person_answer_inserted_before = True
                continue

            elif (
                random.uniform(0, 1) < context_threshold
                and not first_person_query_inserted_before
            ):
                if random.choice([1, 0]):
                    new_dialogue += f"{second} remembers: " + fp_context + "\n"
                    first_person_query = first_person_query.replace(
                        f"{second}:", f"{second}: [factual]"
                    )

                else:
                    new_dialogue += f"{first}: " + fp_context + "\n"
                    first_person_query = first_person_query.replace(
                        f"{second}:", f"{second}: [answer in conversation]"
                    )

                new_dialogue += first_person_query
                first_person_answer_inserted_before = True

        new_item["dialogue"] = (
            "In the dialogue below some people are talking:\n"
            + substitute_pronouns_with_speaker_names(new_dialogue)
        )
        new_train_set.append(new_item)

    json.dump(new_train_set, open(os.path.join(_path, "data/dialogues.json"), "w"))
