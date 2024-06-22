from logging import getLogger

from wafl.readers.base_reader import BaseReader

_logger = getLogger(__name__)


class TextReader(BaseReader):
    def __init__(self, chunk_size: int, overlap: int):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def get_chunks(self, filename):
        _logger.info(f"Reading text file: {filename}")
        with open(filename, "r") as file:
            return self._chunk_text(file.read(), self.chunk_size, self.overlap)


