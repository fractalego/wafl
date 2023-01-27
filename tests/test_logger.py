import os

from unittest import TestCase
from wafl.logger.local_file_logger import LocalFileLogger

_path = os.path.dirname(__file__)


class TestLogger(TestCase):
    def test__setting_depth_to_zero(self):
        logger = LocalFileLogger()
        logger.set_depth(0)

    def test__setting_logger_level(self):
        logger = LocalFileLogger()
        logger.set_log_level(logger.level.INFO)

    def test__write_to_log(self):
        logger = LocalFileLogger()
        logger.write("Hello logs")
