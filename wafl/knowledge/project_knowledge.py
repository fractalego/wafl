from typing import Dict, Any, List

from wafl.knowledge.base_knowledge import BaseKnowledge
from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.parsing.rules_parser import get_dependency_list


class ProjectKnowledge(BaseKnowledge):
    def __init__(self, rules_filename, logger=None):
        self._logger = logger
        self._dependency_dict = {}
        self._knowledge_dict = self._populate_knowledge_structure(
            rules_filename, self._dependency_dict
        )

    def add(self, text, knowledge_name=None):
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        self._knowledge_dict[knowledge_name].add(text, knowledge_name=knowledge_name)

    def ask_for_facts(self, query, is_from_user=False, knowledge_name=None):
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        to_return = []
        for name in self._knowledge_dict.keys():
            if name in self._dependency_dict[knowledge_name]:
                to_return.extend(
                    self._knowledge_dict[knowledge_name].ask_for_facts(
                        query, is_from_user
                    )
                )

        return to_return

    def ask_for_facts_with_threshold(
        self, query, is_from_user=False, knowledge_name=None
    ):
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        to_return = []
        for name in self._knowledge_dict.keys():
            if name in self._dependency_dict[knowledge_name]:
                to_return.extend(
                    self._knowledge_dict[knowledge_name].ask_for_facts_with_threshold(
                        query, is_from_user
                    )
                )

        return to_return

    def ask_for_rule_backward(self, query, knowledge_name=None):
        if not knowledge_name:
            knowledge_name = self.root_knowledge

        rules_list = []

        for name in self._knowledge_dict.keys():
            if name in self._get_all_dependency_names(knowledge_name):
                rules_list.extend(
                    self._knowledge_dict[name].ask_for_rule_backward(query)
                )

        return rules_list

    def _populate_knowledge_structure(
        self, filename: str, dependency_dict: Dict[str, List[str]]
    ) -> Dict[str, SingleFileKnowledge]:
        knowledge_structure = {}
        text = open(filename).read()
        name = "/" + "/".join(filename.split("/")[:-1])
        knowledge_structure[name] = SingleFileKnowledge(
            text, knowledge_name=name, logger=self._logger
        )
        dependencies = get_dependency_list(text)
        dependency_dict.setdefault(name, [])
        dependency_dict[name].extend(
            [self.root_knowledge + item for item in dependencies]
        )
        for dependency_name in dependencies:
            knowledge_structure.update(
                self._populate_knowledge_structure(
                    f"{dependency_name}/rules.wafl", dependency_dict
                )
            )

        return knowledge_structure

    def _get_all_dependency_names(self, knowledge_name):
        all_dependencies = [knowledge_name]
        old_len = 0
        while len(all_dependencies) != old_len:
            for dependency in all_dependencies:
                if dependency in self._dependency_dict:
                    all_dependencies.extend(self._dependency_dict[dependency])

            old_len = len(all_dependencies)

        return all_dependencies
