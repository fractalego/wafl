from wafl.readers.pdf_reader import PdfReader
from wafl.readers.text_reader import TextReader


class ReaderFactory:
    _chunk_size = 1000
    _overlap = 100
    
    @staticmethod
    def get_reader(filename):
        if ".pdf" in filename.lower():
            return PdfReader(ReaderFactory._chunk_size, ReaderFactory._overlap)
        else:
            return TextReader(ReaderFactory._chunk_size, ReaderFactory._overlap)

