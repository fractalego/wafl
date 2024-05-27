import re
import traceback

from importlib import import_module
from inspect import getmembers, isfunction
from wafl.answerer.base_answerer import BaseAnswerer
from wafl.answerer.rule_maker import RuleMaker
from wafl.connectors.clients.llm_chitchat_answer_client import LLMChitChatAnswerClient
from wafl.exceptions import CloseConversation
from wafl.extractors.dataclasses import Query, Answer
from wafl.interface.conversation import Conversation, Utterance
from wafl.simple_text_processing.questions import is_question


class DialogueAnswerer(BaseAnswerer):
    def __init__(self, config, knowledge, interface, code_path, logger):
        self._delete_current_rule = "[delete_rule]"
        self._client = LLMChitChatAnswerClient(config)
        self._knowledge = knowledge
        self._logger = logger
        self._interface = interface
        self._max_num_past_utterances = 5
        self._max_num_past_utterances_for_facts = 5
        self._max_num_past_utterances_for_rules = 0
        self._prior_facts_with_timestamp = []
        self._init_python_module(code_path.replace(".py", ""))
        self._prior_rules = []
        self._max_predictions = 3
        self._rule_creator = RuleMaker(
            knowledge,
            config,
            interface,
            max_num_rules=1,
            delete_current_rule=self._delete_current_rule,
        )

    async def answer(self, query_text):
        if self._logger:
            self._logger.write(f"Dialogue Answerer: the query is {query_text}")

        query = Query.create_from_text("The user says: " + query_text)
        rules_text = await self._get_relevant_rules(query)
        conversation = self._interface.get_utterances_list_with_timestamp().get_last_n(
            self._max_num_past_utterances
        )
        if not conversation:
            conversation = Conversation(
                [
                    Utterance(
                        query_text,
                        "user",
                    )
                ]
            )

        last_bot_utterances = conversation.get_last_speaker_utterances("bot", 3)
        last_user_utterance = conversation.get_last_speaker_utterances("user", 1)
        if not last_user_utterance:
            last_user_utterance = query_text

        conversational_timestamp = len(conversation)
        facts = await self._get_relevant_facts(
            query,
            has_prior_rules=bool(rules_text),
            conversational_timestamp=conversational_timestamp,
        )

        final_answer_text = ""
        for _ in range(self._max_predictions):
            original_answer_text = await self._client.get_answer(
                text=facts,
                rules_text=rules_text,
                dialogue=conversation,
            )
            await self._interface.add_fact(f"The bot predicts: {original_answer_text}")
            (
                answer_text,
                memories,
            ) = await self._substitute_memory_in_answer_and_get_memories_if_present(
                await self._substitute_results_in_answer(original_answer_text)
            )
            if answer_text in last_bot_utterances:
                conversation = Conversation(
                    [
                        Utterance(
                            last_user_utterance[-1],
                            "user",
                        )
                    ]
                )
                continue

            if self._delete_current_rule in answer_text:
                self._prior_rules = []
                final_answer_text += answer_text
                break

            final_answer_text += answer_text
            if not memories:
                break

            facts += "\n" + "\n".join(memories)

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

        if self._logger:
            self._logger.write(
                f"Answer within dialogue: The answer is {final_answer_text}"
            )

        return Answer.create_from_text(final_answer_text)

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
            query, is_from_user=True, threshold=0.85
        )
        if facts_and_thresholds:
            facts = [
                item[0].text
                for item in facts_and_thresholds
                if item[0].text not in memory
            ]
            self._prior_facts_with_timestamp.extend(
                (item, conversational_timestamp) for item in facts
            )
            memory = "\n".join([item[0] for item in self._prior_facts_with_timestamp])
            await self._interface.add_fact(f"The bot remembers the facts:\n{memory}")

        else:
            if is_question(query.text) and not has_prior_rules:
                memory += (
                    f"\nThe answer to {query.text} is not in the knowledge base."
                    "The bot can answer the question while informing the user that the answer was not retrieved"
                )

        return memory

    async def _get_relevant_rules(self, query):
        rules = await self._rule_creator.create_from_query(query)
        for rule in rules:
            if rule not in self._prior_rules:
                self._prior_rules.append(rule)
        return self._prior_rules

    def _init_python_module(self, module_name):
        self._module = import_module(module_name)
        self._functions = [item[0] for item in getmembers(self._module, isfunction)]

    async def _substitute_results_in_answer(self, answer_text):
        matches = re.finditer(
            r"<execute>(.*?)</execute>|<execute>(.*?\))$",
            answer_text,
            re.DOTALL | re.MULTILINE,
        )
        for match in matches:
            to_execute = match.group(1)
            if not to_execute:
                continue
            result = await self._run_code(to_execute)
            answer_text = answer_text.replace(match.group(0), result)

        matches = re.finditer(
            r"<execute>(.*?\))$", answer_text, re.DOTALL | re.MULTILINE
        )
        for match in matches:
            to_execute = match.group(1)
            if not to_execute:
                continue
            result = await self._run_code(to_execute)
            answer_text = answer_text.replace(match.group(0), result)

        return answer_text

    async def _substitute_memory_in_answer_and_get_memories_if_present(
        self, answer_text
    ):
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
        matches = re.finditer(
            r"<remember>(.*?)$", answer_text, re.DOTALL | re.MULTILINE
        )
        memories = []
        for match in matches:
            to_substitute = match.group(1)
            if not to_substitute:
                continue
            answer_text = answer_text.replace(match.group(0), "[Output in memory]")
            memories.append(to_substitute)

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
                    f"Error while executing\n\n```python\n{to_execute}\n```\n\n{str(e)}"
                )
                traceback.print_exc()
                break

        if not result:
            result = f"\n```python\n{to_execute}\n```"

        return result
