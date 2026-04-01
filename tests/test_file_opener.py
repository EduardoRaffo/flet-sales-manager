"""
Tests para utils/file_opener.py — Apertura cross-platform de archivos.
"""

import unittest
from unittest.mock import patch, MagicMock
from utils.file_opener import open_file_cross_platform


class TestOpenFileCrossPlatform(unittest.TestCase):
    """Tests para open_file_cross_platform()."""

    @patch("utils.file_opener.os.startfile")
    def test_windows_uses_startfile(self, mock_startfile):
        open_file_cross_platform("/tmp/test.html")
        mock_startfile.assert_called_once_with("/tmp/test.html")

    @patch("utils.file_opener.subprocess.run")
    @patch("utils.file_opener.os.startfile", side_effect=AttributeError)
    def test_fallback_to_subprocess(self, mock_startfile, mock_run):
        open_file_cross_platform("/tmp/test.html")
        mock_run.assert_called_once_with(["open", "/tmp/test.html"])

    @patch("utils.file_opener.logger")
    @patch("utils.file_opener.subprocess.run", side_effect=Exception("fail"))
    @patch("utils.file_opener.os.startfile", side_effect=AttributeError)
    def test_logs_warning_on_failure(self, mock_startfile, mock_run, mock_logger):
        open_file_cross_platform("/tmp/test.html")
        mock_logger.warning.assert_called_once()


if __name__ == "__main__":
    unittest.main()
