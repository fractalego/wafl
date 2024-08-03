from logging import getLogger
from typing import List

from wafl.data_objects.facts import Fact, Sources
from wafl.readers.base_reader import BaseReader

_logger = getLogger(__name__)


class TextReader(BaseReader):
    def __init__(self, chunk_size: int, overlap: int):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def get_chunks(self, filename: str) -> List[Fact]:
        _logger.info(f"Reading text file: {filename}")
        with open(filename, "r") as file:
            chunks = self._chunk_text(file.read(), self.chunk_size, self.overlap)
            return [
                Fact(
                    text=chunk,
                    metadata={"filename": filename, "chunk_number": i},
                    source=Sources.FROM_TEXT,
                )
                for i, chunk in enumerate(chunks)
            ]
