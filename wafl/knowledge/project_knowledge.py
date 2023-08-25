from typing import Dict, List
from wafl.knowledge.base_knowledge import BaseKnowledge
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.knowledge.utils import get_first_cluster_of_rules
from wafl.parsing.rules_parser import get_dependency_list


class ProjectKnowledge(BaseKnowledge):
    def __init__(self, config, rules_filename=None, logger=None):
        self._config = config
        self._logger = logger
        self._dependency_dict = {}
        self._knowledge_dict = {}
        self.rules_filename = None
        if rules_filename:
            self._knowledge_dict = self._populate_knowledge_structure(
                rules_filename, self._dependency_dict
            )
            self.rules_filename = rules_filename

    async def add(self, text, knowledge_name=None):
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        await self._knowledge_dict[knowledge_name].add(
            text, knowledge_name=knowledge_name
        )

    async def add_rule(self, text, knowledge_name=None):
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        await self._knowledge_dict[knowledge_name].add_rule(
            text, knowledge_name=knowledge_name
        )

    async def ask_for_facts(self, query, is_from_user=False, knowledge_name=None):
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        to_return = []
        for name in self._knowledge_dict.keys():
            if name in self._dependency_dict[knowledge_name]:
                if self._logger:
                    self._logger.write(f"Project Knowledge: Asking for facts in {name}")

                to_return.extend(
                    await self._knowledge_dict[name].ask_for_facts(query, is_from_user)
                )

        return to_return

    async def ask_for_facts_with_threshold(
        self, query, is_from_user=False, knowledge_name=None, threshold=None
    ):
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        to_return = []
        for name in self._knowledge_dict.keys():
            if name in self._get_all_dependency_names(knowledge_name):
                if self._logger:
                    self._logger.write(f"Project Knowledge: Asking for facts in {name}")

                to_return.extend(
                    await self._knowledge_dict[name].ask_for_facts_with_threshold(
                        query, is_from_user, threshold=threshold
                    )
                )

        return sorted(to_return, key=lambda x: -x[1])

    async def ask_for_rule_backward(self, query, knowledge_name=None, first_n=None):
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        rules_and_scores_list = []

        for name in self._knowledge_dict.keys():
            if name in self._get_all_dependency_names(knowledge_name):
                if self._logger:
                    self._logger.write(f"Project Knowledge: Asking for rules in {name}")

                rules_and_scores_list.extend(
                    await self._knowledge_dict[name]._ask_for_rule_backward_with_scores(
                        query, knowledge_name=name, first_n=first_n
                    )
                )

        rules_and_scores_list = sorted(rules_and_scores_list, key=lambda x: -x[1])
        rules = get_first_cluster_of_rules(rules_and_scores_list)[:first_n]
        return rules

    async def has_better_match(
        self, query_text: str, knowledge_name: str = None
    ) -> bool:
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        result_list = []

        for name in self._knowledge_dict.keys():
            if self._logger:
                self._logger.write(
                    f"Project Knowledge: Asking for better match in {name}"
                )

            if name in self._get_all_dependency_names(knowledge_name):
                result_list.append(
                    await self._knowledge_dict[name].has_better_match(query_text)
                )

        return any(result_list)

    def reload_rules(self, rules_filename: str):
        self._knowledge_dict = self._populate_knowledge_structure(
            rules_filename, self._dependency_dict
        )

    async def reinitialize_all_retrievers(self):
        for knowledge in self._knowledge_dict.values():
            await knowledge._initialize_retrievers()

    def get_dependencies_list(self):
        return self._get_all_dependency_names(self.root_knowledge)

    @staticmethod
    def create_from_string(config: "Configuration", rules_text: str, knowledge_name: str) -> "ProjectKnowledge":
        knowledge = ProjectKnowledge(config)
        knowledge._knowledge_dict[knowledge_name] = SingleFileKnowledge(config, rules_text)
        return knowledge

    def _populate_knowledge_structure(
        self, filename: str, dependency_dict: Dict[str, List[str]]
    ) -> Dict[str, SingleFileKnowledge]:
        knowledge_structure = {}
        with open(filename) as file:
            text = file.read()

        name = _get_module_name_from_filename(filename)
        knowledge_structure[name] = SingleFileKnowledge(
            self._config, text, knowledge_name=name, logger=self._logger
        )
        dependencies = get_dependency_list(text)
        dependency_dict.setdefault(name, [])
        dependency_dict[name].extend(
            [self.root_knowledge + item for item in dependencies]
        )
        for dependency_name in dependencies:
            knowledge_structure.update(
                self._populate_knowledge_structure(
                    f".{name}/{dependency_name}/rules.wafl", dependency_dict
                )
            )

        return knowledge_structure

    def _get_all_dependency_names(self, knowledge_name):
        all_dependencies = [knowledge_name]
        old_len = 0
        while len(all_dependencies) != old_len:
            for dependency in all_dependencies:
                if dependency in self._dependency_dict:
                    new_dependency_names = [
                        dependency + item for item in self._dependency_dict[dependency]
                    ]
                    new_dependency_names = [
                        item.replace("//", "/") for item in new_dependency_names
                    ]
                    all_dependencies.extend(new_dependency_names)

            old_len = len(all_dependencies)

        return all_dependencies


def _get_module_name_from_filename(filename):
    filename = filename.replace("//", "/")
    return "/" + "/".join(filename.split("/")[1:-1])
