from typing import List, Tuple

from wafl.retriever.base_retriever import BaseRetriever


class StringRetriever(BaseRetriever):
    def __init__(self):
        self._string_dict = {}

    def add_text_and_index(self, text: str, index: str):
        self._string_dict[text.strip()] = index

    def get_indices_and_scores_from_text(self, text: str) -> List[Tuple[str, float]]:
        if text.strip() in self._string_dict:
            return [(self._string_dict[text.strip()], 1)]

        return []
