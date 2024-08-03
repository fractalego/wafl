import pymupdf

from logging import getLogger
from typing import List
from wafl.data_objects.facts import Fact, Sources
from wafl.readers.base_reader import BaseReader

_logger = getLogger(__name__)


class PdfReader(BaseReader):
    def __init__(self, chunk_size: int, overlap: int):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def get_chunks(self, filename: str) -> List[Fact]:
        _logger.info(f"Reading PDF file: {filename}")
        with pymupdf.open(filename) as doc:
            return [
                Fact(
                    text=page.get_text(),
                    metadata={"filename": filename, "page_number": i},
                    source=Sources.FROM_TEXT,
                )
                for i, page in enumerate(doc)
            ]
