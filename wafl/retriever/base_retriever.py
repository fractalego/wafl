from typing import List, Tuple


class BaseRetriever:
    def add_text_and_index(self, text: str, index: str):
        raise NotImplemented

    def get_indices_and_scores_from_text(self, text: str) -> List[Tuple[str, float]]:
        raise NotImplemented
