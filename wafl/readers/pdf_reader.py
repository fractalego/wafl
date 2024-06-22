from logging import getLogger

from wafl.readers.base_reader import BaseReader

_logger = getLogger(__name__)


class PdfReader(BaseReader):
    def __init__(self, chunk_size: int, overlap: int):
        self.chunk_size = chunk_size
        self.overlap = overlap

    def get_chunks(self, filename):
        _logger.info(f"Reading PDF file: {filename}")

