import re
import time
import traceback

from importlib import import_module
from inspect import getmembers, isfunction
from wafl.answerer.base_answerer import BaseAnswerer
from wafl.connectors.bridges.llm_chitchat_answer_bridge import LLMChitChatAnswerBridge
from wafl.extractors.dataclasses import Query, Answer
from wafl.inference.utils import cluster_facts
from wafl.simple_text_processing.deixis import from_user_to_bot
from wafl.simple_text_processing.questions import is_question

class DialogueAnswerer(BaseAnswerer):
    def __init__(self, config, knowledge, interface, code_path, logger):
        self._bridge = LLMChitChatAnswerBridge(config)
        self._knowledge = knowledge
        self._logger = logger
        self._interface = interface
        self._max_num_past_utterances = 5
        self._max_num_past_utterances_for_facts = 5
        self._max_num_past_utterances_for_rules = 1
        self._prior_facts = []
        self._prior_rules = []
        self._init_python_module(code_path.replace(".py", ""))

    async def answer(self, query_text, policy):
        print(__name__)
        if self._logger:
            self._logger.write(f"Dialogue Answerer: the query is {query_text}")

        query = Query.create_from_text(from_user_to_bot(query_text))
        rules_texts = await self._get_relevant_rules(query)
        facts = await self._get_relevant_facts(query, has_prior_rules=bool(rules_texts))

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
        dialogue_items = [item[1] for item in dialogue_items if item[0] >= start_time]
        dialogue_items = "\n".join(dialogue_items)
        answer_text = await self._bridge.get_answer(
            text=facts,
            dialogue=dialogue_items,
            query=rules_texts if rules_texts else "No specific rules.",
        )
        answer_text = await self._substitute_results_in_answer(answer_text)
        if self._logger:
            self._logger.write(f"Answer within dialogue: The answer is {answer_text}")

        if await policy.accept(answer_text):
            return Answer.create_from_text(answer_text)

        return Answer.create_neutral()

    async def _get_relevant_facts(self, query, has_prior_rules):
        facts_and_thresholds = await self._knowledge.ask_for_facts_with_threshold(
            query, is_from_user=True, knowledge_name="/", threshold=0.7
        )
        texts = cluster_facts(facts_and_thresholds)
        for text in texts[::-1]:
            await self._interface.add_fact(f"The bot remembers: {text}")

        if texts:
            self._prior_facts = self._prior_facts[
                -self._max_num_past_utterances_for_facts :
            ]
            self._prior_facts.append("\n".join(texts))
            facts = "\n".join(self._prior_facts)

        else:
            self._prior_facts = self._prior_facts[-self._max_num_past_utterances :]
            facts = "\n".join(
                self._prior_facts
                + [
                    f"The answer to {query.text} is not in the knowledge base."
                    "The bot can answer the question while informing the user that the answer was not retrieved"
                ]
                if is_question(query.text) and not has_prior_rules
                else []
            )

        return facts

    async def _get_relevant_rules(self, query, max_num_rules=2):
        rules = await self._knowledge.ask_for_rule_backward(
            query,
            knowledge_name="/",
        )
        rules = rules[:max_num_rules]
        rules_texts = []
        for rule in rules:
            rules_text = f"- If {rule.effect.text}:\n"
            for causes in rule.causes:
                rules_text += f"    {causes.text}\n"

            if any(rules_text in item for item in self._prior_rules):
                continue

            rules_texts.append(rules_text)
            self._interface.add_fact(f"The bot remembers the rule: {rules_text}")

        self._prior_rules = self._prior_rules[
            -self._max_num_past_utterances_for_rules :
        ]

        if rules_texts:
            self._prior_rules.append("".join(rules_texts))
            rules_texts = "".join(set(self._prior_rules))

        else:
            rules_texts = "".join(self._prior_rules)

        return rules_texts

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

    async def _run_code(self, to_execute):
        result = None
        try:
            if any(item + "(" in to_execute for item in self._functions):
                result = eval(f"self._module.{to_execute}")

        except Exception as e:
            traceback.print_exc()
            result = f"Error in the code to execute: {str(e)}"

        if not result:
            result = "unknown"

        return result
