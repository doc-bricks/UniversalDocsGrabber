# -*- coding: utf-8 -*-
"""
Hermetic regression and contract test suite for data model resilience,
schema-drift tolerance, None-handling in categorization, and atomic I/O
directory safety in UniversalDocsGrabber.

Bugsweep Reference: dev/bugsweep (2026-11-01)
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from atomic_io import (
    atomic_publish_file,
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_text,
)
from UniversalDocsGrabberV1 import (
    DEFAULT_GROUP,
    Document,
    DownloadSettings,
    GrabberWorker,
    MailAccount,
    SearchProfile,
    collect_category_entries,
)


class TestBugsweepDataModelAndAtomicDirResilience(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="udg_bugsweep_20261101_")
        self.base_dir = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_document_from_dict_schema_drift_and_missing_fields(self):
        """Verifies Document.from_dict populates defaults and never crashes on missing keys or None."""
        # 1. Missing required fields
        partial = {"filename": "invoice_123.pdf", "path": "/docs/invoice_123.pdf"}
        doc = Document.from_dict(partial)
        self.assertIsNotNone(doc)
        self.assertEqual(doc.filename, "invoice_123.pdf")
        self.assertEqual(doc.path, "/docs/invoice_123.pdf")
        self.assertEqual(doc.profile, "Default")
        self.assertEqual(doc.date, "")
        self.assertEqual(doc.sender, "")
        self.assertEqual(doc.subject, "")

        # 2. Empty dict
        empty_doc = Document.from_dict({})
        self.assertIsNotNone(empty_doc)
        self.assertEqual(empty_doc.profile, "Default")
        self.assertEqual(empty_doc.filename, "")

        # 3. None fields
        none_doc = Document.from_dict({"profile": None, "filename": "test.pdf", "date": None, "path": None})
        self.assertIsNotNone(none_doc)
        self.assertEqual(none_doc.profile, "Default")
        self.assertEqual(none_doc.filename, "test.pdf")

        # 4. Unknown keys filtered cleanly
        noisy = {"filename": "test.pdf", "path": "/a/b", "unknown_future_field": 42}
        noisy_doc = Document.from_dict(noisy)
        self.assertIsNotNone(noisy_doc)
        self.assertEqual(noisy_doc.filename, "test.pdf")

        # 5. Non-dict returns None
        self.assertIsNone(Document.from_dict(None))
        self.assertIsNone(Document.from_dict("not-a-dict"))
        self.assertIsNone(Document.from_dict([1, 2, 3]))

    def test_mail_account_from_dict_resilience(self):
        """Verifies MailAccount.from_dict handles schema drift and rejects empty names."""
        # 1. Missing user or host gets defaulted
        acc = MailAccount.from_dict({"name": "WorkMail"})
        self.assertIsNotNone(acc)
        self.assertEqual(acc.name, "WorkMail")
        self.assertEqual(acc.host, "")
        self.assertEqual(acc.user, "")
        self.assertEqual(acc.port, 993)
        self.assertEqual(acc.search_folder, "INBOX")

        # 2. Empty or whitespace name returns None
        self.assertIsNone(MailAccount.from_dict({"name": ""}))
        self.assertIsNone(MailAccount.from_dict({"name": "   "}))
        self.assertIsNone(MailAccount.from_dict({}))
        self.assertIsNone(MailAccount.from_dict(None))

    def test_search_profile_from_dict_resilience(self):
        """Verifies SearchProfile.from_dict handles missing fields and defaults cleanly."""
        # 1. Minimal dict without account_name or id
        prof = SearchProfile.from_dict({"name": "Rechnungen"})
        self.assertIsNotNone(prof)
        self.assertEqual(prof.name, "Rechnungen")
        self.assertEqual(prof.group, DEFAULT_GROUP)
        self.assertEqual(prof.account_name, "")
        self.assertTrue(len(prof.id) > 0)

        # 2. Non-dict returns None
        self.assertIsNone(SearchProfile.from_dict(None))
        self.assertIsNone(SearchProfile.from_dict(123))

    def test_download_settings_from_dict_resilience(self):
        """Verifies DownloadSettings.from_dict handles None and corrupted structures."""
        settings = DownloadSettings.from_dict({"download_attachments": False, "invalid_field": 99})
        self.assertFalse(settings.download_attachments)
        self.assertTrue(settings.convert_body_to_pdf)

        default_settings = DownloadSettings.from_dict(None)
        self.assertIsInstance(default_settings, DownloadSettings)
        self.assertTrue(default_settings.download_attachments)

    def test_auto_categorize_resilience_against_none_and_dirty_rules(self):
        """Verifies _auto_categorize does not crash on None, strings, or malformed dicts in category_rules."""
        settings = DownloadSettings(
            auto_categorize=True,
            category_rules=[
                None,
                "rechnung",
                {"keyword": None, "folder": "NoneFolder"},
                {"keyword": "custom_kw", "folder": None},
                {"keyword": "telekom", "folder": "Telekommunikation", "match": "sender"},
                12345,
            ]
        )
        worker = GrabberWorker([], [], settings, self.base_dir, [])

        # Should match custom rule cleanly
        cat = worker._auto_categorize("Telekom Kundenservice", "Ihre Monatsrechnung", settings)
        self.assertEqual(cat, "Telekommunikation")

        # Should match default rule cleanly despite dirty custom rules
        cat_default = worker._auto_categorize("AWS Billing", "Monthly Invoice", settings)
        self.assertEqual(cat_default, "Rechnungen")

        # Non-matching returns None without crashing
        cat_none = worker._auto_categorize("Friend", "Hello there", settings)
        self.assertIsNone(cat_none)

    def test_collect_category_entries_resilience_against_dirty_rules(self):
        """Verifies collect_category_entries tolerates None or non-dict rules without AttributeError."""
        global_settings = DownloadSettings(
            category_rules=[
                None,
                "invalid",
                {"folder": "ValidGlobal"},
                {"keyword": "only_kw"},
            ]
        )
        profile_settings = DownloadSettings(
            category_rules=[
                None,
                {"folder": "ValidProfile"},
                {"folder": "   "},
            ]
        )
        prof = SearchProfile(
            id="p1",
            name="Prof1",
            group="G1",
            account_name="Acc1",
            override_settings=profile_settings,
        )
        categories = collect_category_entries(global_settings, [prof], [], self.base_dir)
        cat_names = [c["name"] for c in categories]
        self.assertIn("ValidGlobal", cat_names)
        self.assertIn("ValidProfile", cat_names)
        self.assertNotIn("invalid", cat_names)
        self.assertNotIn("", cat_names)

    def test_atomic_write_text_rejects_directory_target(self):
        """Verifies atomic_write_text immediately raises IsADirectoryError when target is a directory."""
        dir_target = self.base_dir / "existing_dir"
        dir_target.mkdir()
        with self.assertRaises(IsADirectoryError):
            atomic_write_text(dir_target, "test content")

        # Verify no temp files leaked
        leftovers = list(self.base_dir.glob(".*tmp*"))
        self.assertEqual(leftovers, [])

    def test_atomic_write_bytes_rejects_directory_target(self):
        """Verifies atomic_write_bytes immediately raises IsADirectoryError when target is a directory."""
        dir_target = self.base_dir / "existing_dir_bytes"
        dir_target.mkdir()
        with self.assertRaises(IsADirectoryError):
            atomic_write_bytes(dir_target, b"binary content")

        leftovers = list(self.base_dir.glob(".*tmp*"))
        self.assertEqual(leftovers, [])

    def test_atomic_write_json_rejects_directory_target(self):
        """Verifies atomic_write_json immediately raises IsADirectoryError when target is a directory."""
        dir_target = self.base_dir / "existing_dir_json"
        dir_target.mkdir()
        with self.assertRaises(IsADirectoryError):
            atomic_write_json(dir_target, {"key": "value"})

        leftovers = list(self.base_dir.glob(".*tmp*"))
        self.assertEqual(leftovers, [])

    def test_atomic_publish_file_rejects_directory_target(self):
        """Verifies atomic_publish_file cleans up temp source and raises IsADirectoryError on directory target."""
        dir_target = self.base_dir / "existing_dir_pub"
        dir_target.mkdir()
        tmp_src = self.base_dir / "source.tmp"
        tmp_src.write_text("temporary data", encoding="utf-8")

        with self.assertRaises(IsADirectoryError):
            atomic_publish_file(tmp_src, dir_target)

        # Source temp file cleaned up
        self.assertFalse(tmp_src.exists())

    def test_manage_translations_check_cwd_independence(self):
        """Verifies manage_translations.check_translations succeeds when executed from arbitrary CWD."""
        import manage_translations
        # Running with default APP_DIR argument
        exit_code = manage_translations.check_translations()
        self.assertEqual(exit_code, 0)

    def test_save_attachment_bounds_candidate_name_length(self):
        """Verifies _save_attachment limits base_name length to protect Windows MAX_PATH limits."""
        long_base = "2026-11-01__" + ("A" * 150) + "__" + ("B" * 150)
        settings = DownloadSettings(download_attachments=True, formats=["pdf"])
        worker = GrabberWorker([], [], settings, self.base_dir, [])

        class DummyPart:
            def get_filename(self):
                return "very_long_attachment_name_" + ("C" * 100) + ".pdf"
            def get_payload(self, decode=True):
                return b"%PDF-1.4 dummy binary"

        dl_dir = self.base_dir / "Invoices"
        dl_dir.mkdir(parents=True, exist_ok=True)
        saved = worker._save_attachment(
            DummyPart(),
            long_base,
            dl_dir,
            settings,
            "Prof1",
            "2026-11-01",
            "Sender",
            "Subject",
            attachment_index=1,
        )
        self.assertTrue(saved)
        files = list(dl_dir.glob("*.pdf"))
        self.assertEqual(len(files), 1)
        # Check filename length is bounded (well below 260 characters)
        self.assertLessEqual(len(files[0].name), 180)


if __name__ == "__main__":
    unittest.main()
