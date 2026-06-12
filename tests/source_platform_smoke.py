"""Cross-platform source smoke tests for UniversalDocsGrabber."""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from PySide6.QtWidgets import QApplication

import UniversalDocsGrabberV1 as app


class SourcePlatformSmokeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.qt_app = QApplication.instance() or QApplication([])

    def test_main_window_roundtrip_uses_temp_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            original_config = app.CONFIG_FILE
            original_docs_db = app.DOCS_DB

            try:
                app.CONFIG_FILE = tmp_path / "config_v1.json"
                app.DOCS_DB = tmp_path / "documents.json"

                window = app.MainWindow()
                window.base_path = str(tmp_path / "exports")
                window.scheduler_interval = 30
                window.accounts = [
                    app.MailAccount("Primary", "imap.example.org", "user@example.org")
                ]
                window.profiles = [
                    app.SearchProfile(
                        "profile-1",
                        "Invoices",
                        "Finance",
                        "Primary",
                        query_subject="Invoice",
                    )
                ]
                window.documents = [
                    app.Document(
                        "Invoices",
                        "rechnung.pdf",
                        "2026-06-05",
                        str(tmp_path / "exports" / "rechnung.pdf"),
                    )
                ]
                window.save_config()
                window.close()

                reloaded = app.MainWindow()
                self.assertEqual(reloaded.base_path, str(tmp_path / "exports"))
                self.assertEqual(reloaded.scheduler_interval, 30)
                self.assertEqual(len(reloaded.accounts), 1)
                self.assertEqual(reloaded.accounts[0].host, "imap.example.org")
                self.assertEqual(len(reloaded.profiles), 1)
                self.assertEqual(reloaded.profiles[0].query_subject, "Invoice")
                self.assertEqual(len(reloaded.documents), 1)
                self.assertEqual(reloaded.documents[0].filename, "rechnung.pdf")
                reloaded.close()
            finally:
                app.CONFIG_FILE = original_config
                app.DOCS_DB = original_docs_db

    def test_non_windows_word_conversion_degrades_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            dummy_docx = tmp_path / "probe.docx"
            dummy_docx.write_text("placeholder", encoding="utf-8")
            log_messages: list[str] = []
            converter = app.UniversalConverter(log_messages.append)
            original_win32_available = app.WIN32_AVAILABLE
            original_docx2pdf_available = app.DOCX2PDF_AVAILABLE

            try:
                app.WIN32_AVAILABLE = False
                app.DOCX2PDF_AVAILABLE = False
                result = converter.convert_word(
                    str(dummy_docx),
                    str(tmp_path / "probe.pdf"),
                )
            finally:
                app.WIN32_AVAILABLE = original_win32_available
                app.DOCX2PDF_AVAILABLE = original_docx2pdf_available

            self.assertFalse(result)
            self.assertTrue(
                any("Word-Konverter nicht verfügbar" in msg for msg in log_messages)
            )

    def test_missing_ocr_stack_reports_clear_result(self) -> None:
        log_messages: list[str] = []
        ocr = app.OCRProcessor(log_messages.append)
        original_ocr_available = app.OCR_AVAILABLE

        try:
            app.OCR_AVAILABLE = False
            ok, detail = ocr.add_text_layer(Path("scan.pdf"))
        finally:
            app.OCR_AVAILABLE = original_ocr_available

        self.assertFalse(ok)
        self.assertEqual(detail, "No OCR")
        self.assertTrue(
            any("OCR nicht verfügbar" in message for message in log_messages)
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
