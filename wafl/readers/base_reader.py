from typing import List

from wafl.data_objects.facts import Fact


class BaseReader:
    def read(self, file_path: str) -> str:
        raise NotImplementedError()

    def get_chunks(self, filename: str) -> List[Fact]:
        raise NotImplementedError()

    def _chunk_text(self, text: str, size: int, overlap: int) -> List[str]:
        chunks = []
        for i in range(0, len(text), size - overlap):
            chunks.append(text[i : i + size])
        return chunks
