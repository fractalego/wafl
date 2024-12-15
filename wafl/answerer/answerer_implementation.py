import re

from typing import List, Tuple
from wafl.answerer.entailer import Entailer
from wafl.exceptions import CloseConversation
from wafl.data_objects.facts import Fact, Sources
from wafl.interface.conversation import Conversation, Utterance


def is_executable(text: str) -> bool:
    return "<execute>" in text


def create_one_liner(query_text):
    return Conversation(
        [
            Utterance(
                query_text,
                "user",
            )
        ]
    )


async def substitute_memory_in_answer_and_get_memories_if_present(
    answer_text: str,
) -> Tuple[str, List[str]]:
    matches = re.finditer(
        r"<remember>(.*?)</remember>|<remember>(.*?)$",
        answer_text,
        re.DOTALL | re.MULTILINE,
    )
    memories = []
    for match in matches:
        to_substitute = match.group(1)
        if not to_substitute:
            continue
        answer_text = answer_text.replace(match.group(0), "[Output in memory]")
        memories.append(to_substitute)

    answer_text = answer_text.replace("<br>", "\n")
    matches = re.finditer(r"<remember>(.*?)$", answer_text, re.DOTALL | re.MULTILINE)
    memories = []
    for match in matches:
        to_substitute = match.group(1)
        if not to_substitute:
            continue
        answer_text = answer_text.replace(match.group(0), "[Output in memory]")
        memories.append(to_substitute)

    return answer_text, memories


async def execute_results_in_answer(answer_text: str, module, functions) -> str:
    if "<execute>" in answer_text and "</execute>" not in answer_text:
        answer_text += "</execute>"

    matches = re.finditer(
        r"<execute>(.*?)</execute>",
        answer_text,
        re.DOTALL | re.MULTILINE,
    )
    for match in matches:
        to_execute = match.group(1)
        if not to_execute:
            continue
        result = await _run_code(to_execute, module, functions)
        answer_text = answer_text.replace(match.group(0), result)

    return answer_text


async def _run_code(to_execute: str, module, functions) -> str:
    result = None
    for _ in range(3):
        try:
            if any(item + "(" in to_execute for item in functions):
                result = eval(f"module.{to_execute}")
                break

            else:
                ldict = {}
                exec(to_execute, globals(), ldict)
                if "result" in ldict:
                    result = str(ldict["result"])
                    break

        except NameError as e:
            match = re.search(r"\'(\w+)\' is not defined", str(e))
            if match:
                to_import = match.group(1)
                to_execute = f"import {to_import}\n{to_execute}"

        except CloseConversation as e:
            raise e

        except Exception as e:
            result = (
                f"Error while executing\n\n```python\n{to_execute}\n```\n\n{str(e)}"
            )
            raise RuntimeError(result)

    if not result:
        result = f"\n```python\n{to_execute}\n```"

    return result


def create_memory_from_fact_list(facts: List[Fact], max_num_facts: int) -> str:
    text_fact_list = [
        "\n\n- " + "<item> " + fact.text + " </item>"
        for fact in facts
        if fact.source == Sources.FROM_TEXT
    ][:max_num_facts]
    rule_fact_list = [
        "\n\n- " + "<item> " + fact.text + " </item>"
        for fact in facts
        if fact.source in [None, Sources.FROM_RULES]
    ]
    return "".join(text_fact_list + rule_fact_list)


def get_facts_with_metadata_from_facts_and_thresholds(
    facts_and_thresholds: List[Tuple[Fact, float]], memory: str
) -> List[str]:
    fact_list = []
    for item in facts_and_thresholds:
        if item[0].text not in memory:
            new_fact = item[0].copy()
            if item[0].metadata:
                new_fact.text = new_fact.text
            fact_list.append(new_fact)

    return fact_list


def add_dummy_utterances_to_continue_generation(
    conversation: Conversation, answer_text: str
):
    conversation.add_utterance(
        Utterance(
            answer_text,
            "bot",
        )
    )
    conversation.add_utterance(
        Utterance(
            "Continue",
            "user",
        )
    )


def add_memories_to_facts(facts: str, memories: List[str]) -> str:
    return facts + "\n" + "\n".join(memories)


async def select_best_rules_using_entailer(
    conversation: Conversation,
    rules_as_strings: List[str],
    entailer: Entailer,
    num_rules: int,
) -> List[str]:
    query_text = conversation.get_last_speaker_utterance("user")
    ### Sort rules by score
    scores = []
    for rule in rules_as_strings:
        score = await entailer.get_score(query_text, rule)
        scores.append(score)
    rules_as_strings = sorted(
        rules_as_strings, key=lambda x: scores[rules_as_strings.index(x)], reverse=True
    )
    return rules_as_strings[:num_rules]
