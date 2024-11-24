from importlib import import_module
from inspect import getmembers, isfunction
from typing import List

from wafl.answerer.entailer import Entailer
from wafl.answerer.answerer_implementation import (
    substitute_memory_in_answer_and_get_memories_if_present,
    create_one_liner,
    get_facts_with_metadata_from_facts_and_thresholds,
    add_dummy_utterances_to_continue_generation,
    add_memories_to_facts,
    execute_results_in_answer,
    create_memory_from_fact_list,
    select_best_rules_using_entailer,
)
from wafl.answerer.rule_maker import RuleMaker
from wafl.connectors.clients.llm_chat_client import LLMChatClient
from wafl.data_objects.dataclasses import Query, Answer
from wafl.interface.conversation import Conversation, Utterance
from wafl.simple_text_processing.questions import is_question


class DialogueAnswerer:
    def __init__(self, config, knowledge, interface, code_path, logger):
        self._threshold_for_facts = 0.85
        self._client = LLMChatClient(config)
        self._entailer = Entailer(config)
        self._knowledge = knowledge
        self._logger = logger
        self._interface = interface
        self._max_num_past_utterances = 5
        self._max_num_facts = 5
        self._max_num_rules = 2
        self._prior_facts = []
        self._init_python_module(code_path.replace(".py", ""))
        self._prior_rules = []
        self._max_predictions = 3
        self._rule_creator = RuleMaker(
            knowledge,
            config,
            interface,
            max_num_rules=1,
        )

    def reset(self):
        self._prior_facts = []
        self._prior_rules = []

    async def answer(self, query_text: str) -> Answer:
        if self._logger:
            self._logger.write(f"Dialogue Answerer: the query is {query_text}")
        query = Query.create_from_text("The user says: " + query_text)
        conversation = self._interface.get_utterances_list_with_timestamp().get_last_n(
            self._max_num_past_utterances
        )
        conversation.add_utterance(Utterance(speaker="user", text=query_text))
        rules_text = await self._get_relevant_rules(conversation)
        if not conversation:
            conversation = create_one_liner(query_text)
        memory = await self._get_relevant_facts(
            query,
            has_prior_rules=bool(rules_text),
        )

        final_answer_text = ""
        is_finished = False
        for num_attempts in range(self._max_predictions):
            try:
                original_answer_text = await self._client.get_answer(
                    text=memory,
                    rules_text=rules_text,
                    dialogue=conversation,
                )
                await self._interface.add_fact(
                    f"The bot predicts: {original_answer_text}"
                )
                answer_text, memories = await self._apply_substitutions(
                    original_answer_text
                )

                final_answer_text += answer_text
                if not memories:
                    is_finished = True
                    break
                facts = add_memories_to_facts(facts, memories)
                add_dummy_utterances_to_continue_generation(conversation, answer_text)

            except RuntimeError as e:
                if self._logger:
                    self._logger.write(f"Error in generating answer: {e}")
                conversation.add_utterance(
                    Utterance(
                        speaker="bot",
                        text=f"[when using the answer {original_answer_text} the system says {e}]\n",
                    )
                )

        if not is_finished:
            final_answer_text += "I was unable to generate a full answer. Please see the logs for more information."

        if self._logger:
            self._logger.write(
                f"Answer within dialogue: The answer is {final_answer_text}"
            )

        return Answer.create_from_text(final_answer_text)

    async def _get_relevant_facts(self, query: Query, has_prior_rules: bool) -> str:
        memory = create_memory_from_fact_list(self._prior_facts, self._max_num_facts)
        facts_and_thresholds = await self._knowledge.ask_for_facts_with_threshold(
            query, is_from_user=True, threshold=self._threshold_for_facts
        )
        if facts_and_thresholds:
            facts = get_facts_with_metadata_from_facts_and_thresholds(
                facts_and_thresholds, memory
            )
            self._prior_facts.extend(facts)
            memory = create_memory_from_fact_list(
                self._prior_facts, self._max_num_facts
            )
            await self._interface.add_fact(f"The bot remembers the facts:\n{memory}")

        else:
            if is_question(query.text) and not has_prior_rules:
                memory += (
                    f"\nThe answer to {query.text} is not in the knowledge base."
                    "The bot can answer the question while informing the user that the answer was not retrieved"
                )

        return memory

    async def _get_relevant_rules(self, conversation: Conversation) -> List[str]:
        rules_as_strings = await self._rule_creator.create_from_query(conversation)
        rules_as_strings = await select_best_rules_using_entailer(
            conversation, rules_as_strings, self._entailer, num_rules=1
        )
        for rule in rules_as_strings:
            if rule not in self._prior_rules:
                self._prior_rules.insert(0, rule)
        self._prior_rules = self._prior_rules[: self._max_num_rules]
        return self._prior_rules

    def _init_python_module(self, module_name):
        self._module = import_module(module_name)
        self._functions = [item[0] for item in getmembers(self._module, isfunction)]

    async def _apply_substitutions(self, original_answer_text):
        return await substitute_memory_in_answer_and_get_memories_if_present(
            await execute_results_in_answer(
                original_answer_text,
                self._module,
                self._functions,
            )
        )
