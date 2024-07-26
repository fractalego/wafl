from wafl.readers.pdf_reader import PdfReader
from wafl.readers.text_reader import TextReader


class ReaderFactory:
    _chunk_size = 10000
    _overlap = 500
    _extension_to_reader_dict = {".pdf": PdfReader, ".txt": TextReader}

    @staticmethod
    def get_reader(filename):
        for extension, reader in ReaderFactory._extension_to_reader_dict.items():
            if extension in filename.lower():
                return reader(ReaderFactory._chunk_size, ReaderFactory._overlap)

        return TextReader(ReaderFactory._chunk_size, ReaderFactory._overlap)
