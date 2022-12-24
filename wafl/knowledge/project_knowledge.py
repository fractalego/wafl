from typing import Dict, Any, List

from wafl.knowledge.single_file_knowledge import SingleFileKnowledge
from wafl.parsing.rules_parser import get_dependency_list


class ProjectKnowledge:
    def __init__(self, rules_filename, logger=None):
        self._dependency_dict = {}
        self._knowledge_dict = self._populate_knowledge_structure(
            rules_filename, self._dependency_dict
        )

    def add(self, text):
        raise NotImplementedError()

    def ask_for_facts(self, query, is_from_user=False):
        raise NotImplementedError()

    def ask_for_facts_with_threshold(self, query, is_from_user=False):
        raise NotImplementedError()

    def ask_for_rule_backward(self, query):
        raise NotImplementedError()

    def _populate_knowledge_structure(
        self, filename: str, dependency_dict: Dict[str, List[str]]
    ) -> Dict[str, SingleFileKnowledge]:
        knowledge_structure = {}
        text = open(filename).read()
        knowledge_structure[filename] = SingleFileKnowledge(text)
        dependencies = get_dependency_list(text)
        dependency_dict.setdefault(filename, [])
        dependency_dict[filename].append(dependencies)
        for name in dependencies:
            knowledge_structure.update(
                self._populate_knowledge_structure(
                    f"{name}/rules.wafl", dependency_dict
                )
            )

        return knowledge_structure
