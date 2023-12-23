import re
import time
import traceback

from importlib import import_module
from inspect import getmembers, isfunction

from wafl.answerer.answerer_implementation import (
    get_last_bot_utterances,
    get_last_user_utterance,
)
from wafl.answerer.base_answerer import BaseAnswerer
from wafl.connectors.bridges.llm_chitchat_answer_bridge import LLMChitChatAnswerBridge
from wafl.exceptions import CloseConversation
from wafl.extractors.dataclasses import Query, Answer
from wafl.simple_text_processing.questions import is_question


class DialogueAnswerer(BaseAnswerer):
    def __init__(self, config, knowledge, interface, code_path, logger):
        self._bridge = LLMChitChatAnswerBridge(config)
        self._knowledge = knowledge
        self._logger = logger
        self._interface = interface
        self._max_num_past_utterances = 5
        self._max_num_past_utterances_for_facts = 5
        self._max_num_past_utterances_for_rules = 0
        self._prior_facts_with_timestamp = []
        self._init_python_module(code_path.replace(".py", ""))
        self._max_predictions = 3

    async def answer(self, query_text):
        if self._logger:
            self._logger.write(f"Dialogue Answerer: the query is {query_text}")

        query = Query.create_from_text(query_text)
        rules_texts = await self._get_relevant_rules(query)

        dialogue = self._interface.get_utterances_list_with_timestamp()[
            -self._max_num_past_utterances :
        ]
        start_time = -1
        if dialogue:
            start_time = dialogue[0][0]

        if not dialogue:
            dialogue = [(time.time(), f"user: {query_text}")]

        dialogue_items = dialogue
        dialogue_items = sorted(dialogue_items, key=lambda x: x[0])
        last_bot_utterances = get_last_bot_utterances(dialogue_items, num_utterances=3)
        last_user_utterance = get_last_user_utterance(dialogue_items)
        dialogue_items = [item[1] for item in dialogue_items if item[0] >= start_time]
        conversational_timestamp = len(dialogue_items)
        facts = await self._get_relevant_facts(
            query,
            has_prior_rules=bool(rules_texts),
            conversational_timestamp=conversational_timestamp,
        )
        dialogue_items = "\n".join(dialogue_items)

        for _ in range(self._max_predictions):
            original_answer_text = await self._bridge.get_answer(
                text=facts,
                dialogue=dialogue_items,
                query=rules_texts,
            )
            await self._interface.add_fact(f"The bot predicts: {original_answer_text}")
            (
                answer_text,
                memories,
            ) = await self._substitute_memory_in_answer_and_get_memories_if_present(
                await self._substitute_results_in_answer(original_answer_text)
            )
            if answer_text in last_bot_utterances:
                dialogue_items = last_user_utterance
                continue

            if not memories:
                break

            facts += "\n" + "\n".join(memories)
            dialogue_items += f"\nbot: {original_answer_text}"

        if self._logger:
            self._logger.write(f"Answer within dialogue: The answer is {answer_text}")

        return Answer.create_from_text(answer_text)

    async def _get_relevant_facts(
        self, query, has_prior_rules, conversational_timestamp
    ):
        memory = "\n".join([item[0] for item in self._prior_facts_with_timestamp])
        self._prior_facts_with_timestamp = [
            item
            for item in self._prior_facts_with_timestamp
            if item[1]
            > conversational_timestamp - self._max_num_past_utterances_for_facts
        ]
        facts_and_thresholds = await self._knowledge.ask_for_facts_with_threshold(
            query, is_from_user=True, knowledge_name="/", threshold=0.8
        )
        if facts_and_thresholds:
            facts = [item[0].text for item in facts_and_thresholds if item[0].text not in memory]
            self._prior_facts_with_timestamp.extend(
                (item, conversational_timestamp) for item in facts
            )
            memory = "\n".join([item[0] for item in self._prior_facts_with_timestamp])

        else:
            if is_question(query.text) and not has_prior_rules:
                memory += (
                    f"\nThe answer to {query.text} is not in the knowledge base."
                    "The bot can answer the question while informing the user that the answer was not retrieved"
                )

        if has_prior_rules:
            memory += f"\nThe bot tries to answer {query.text} following the rules from the user."

        return memory

    async def _get_relevant_rules(self, query, max_num_rules=1):
        rules = await self._knowledge.ask_for_rule_backward(
            query,
            knowledge_name="/",
        )
        rules = rules[:max_num_rules]
        rules_texts = []
        for rule in rules:
            rules_text = f"- If {rule.effect.text} go through the following points:\n"
            for cause_index, causes in enumerate(rule.causes):
                rules_text += f"    {cause_index + 1}) {causes.text}\n"

            rules_texts.append(rules_text)
            await self._interface.add_fact(f"The bot remembers the rule:\n{rules_text}")

        return "\n".join(rules_texts)

    def _init_python_module(self, module_name):
        self._module = import_module(module_name)
        self._functions = [item[0] for item in getmembers(self._module, isfunction)]

    async def _substitute_results_in_answer(self, answer_text):
        matches = re.finditer(r"<execute>(.*?)</execute>", answer_text, re.DOTALL)
        for match in matches:
            to_execute = match.group(1)
            result = await self._run_code(to_execute)
            answer_text = answer_text.replace(match.group(0), result)

        return answer_text

    async def _substitute_memory_in_answer_and_get_memories_if_present(
        self, answer_text
    ):
        matches = re.finditer(r"<remember>(.*?)</remember>", answer_text, re.DOTALL)
        memories = []
        for match in matches:
            to_execute = match.group(1)
            answer_text = answer_text.replace(match.group(0), "")
            memories.append(to_execute)

        return answer_text, memories

    async def _run_code(self, to_execute):
        result = None
        for _ in range(3):
            try:
                if any(item + "(" in to_execute for item in self._functions):
                    result = eval(f"self._module.{to_execute}")
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
                    f'Error while executing\n\n"""python\n{to_execute}\n"""\n\n{str(e)}'
                )
                traceback.print_exc()
                break

        if not result:
            result = f'\n"""python\n{to_execute}\n"""'

        return result
