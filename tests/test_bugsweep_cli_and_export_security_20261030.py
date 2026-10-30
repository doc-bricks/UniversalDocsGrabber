# -*- coding: utf-8 -*-
"""
Hermetic regression and contract test suite for CLI export security,
protected path defense, CSV formula injection neutralization, object
compatibility, and destination path resolution.

Bugsweep Reference: dev/bugsweep (2026-10-30)
"""

from __future__ import annotations

import csv
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cli
from UniversalDocsGrabberV1 import (
    Document,
    DownloadSettings,
    MailAccount,
    SearchProfile,
)


class TestBugsweepCliAndExportSecurity(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="udg_sec_bugsweep_")
        self.base_dir = Path(self.temp_dir)
        self.config_file = self.base_dir / "config_v1.json"
        self.docs_db = self.base_dir / "documents.json"
        self.downloads = self.base_dir / "Downloads"
        self.downloads.mkdir(parents=True, exist_ok=True)

        self.sample_config = {
            "base_path": str(self.downloads),
            "scheduler_interval": 10,
            "profiles": [
                {
                    "id": "prof-1",
                    "name": "Rechnungen",
                    "group": "Finance",
                    "account_name": "OfficeMail",
                    "target_folder": "Invoices",
                    "active": True,
                }
            ],
            "accounts": [
                {
                    "name": "OfficeMail",
                    "host": "imap.example.com",
                    "user": "billing@example.com",
                }
            ],
        }
        self.config_file.write_text(json.dumps(self.sample_config), encoding="utf-8")
        self.docs_db.write_text("[]", encoding="utf-8")

    def tearDown(self):
        # Reset permissions if read-only was set
        for p in self.base_dir.rglob("*"):
            try:
                os.chmod(p, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_cli_export_library_rejects_protected_path(self):
        """Facet 1: --export-library must reject overwriting protected config/database files."""
        protected = {self.config_file.resolve(), self.docs_db.resolve()}
        with patch("cli.get_default_protected_paths", return_value=protected):
            exit_code = cli.run_cli([
                "--export-library", str(self.config_file),
                "--config", str(self.config_file),
                "--documents-db", str(self.docs_db),
            ])
            self.assertEqual(exit_code, 1)

            # Protected config file content must remain completely intact
            loaded = json.loads(self.config_file.read_text(encoding="utf-8"))
            self.assertEqual(loaded["scheduler_interval"], 10)
            self.assertEqual(loaded["profiles"][0]["name"], "Rechnungen")

    def test_cli_export_library_handles_readonly_target(self):
        """Facet 2: --export-library uses atomic_write_json and safely replaces read-only targets."""
        target_file = self.base_dir / "readonly_export.json"
        target_file.write_text("{}", encoding="utf-8")
        os.chmod(target_file, stat.S_IREAD)

        try:
            exit_code = cli.run_cli([
                "--export-library", str(target_file),
                "--config", str(self.config_file),
                "--documents-db", str(self.docs_db),
                "--json",
            ])
            self.assertEqual(exit_code, 0)
            data = json.loads(target_file.read_text(encoding="utf-8"))
            self.assertEqual(data["schema"], "docsgrabber-library-v1")
            self.assertEqual(len(data["profiles"]), 1)
        finally:
            os.chmod(target_file, stat.S_IWRITE | stat.S_IREAD)

    def test_csv_export_sanitizes_formula_injection(self):
        """Facet 3: CWE-1236 CSV formula injection triggers must be neutralized with a leading quote."""
        malicious_docs = [
            {
                "date": "2026-10-30",
                "profile": "=HYPERLINK(\"http://evil.com\")",
                "filename": "+calc.pdf",
                "path": str(self.downloads / "calc.pdf"),
                "sender": "@attacker@evil.corp",
                "subject": "-cmd|' /C calc'!A0",
            },
            {
                "date": "2026-10-30",
                "profile": "  =spaced_formula()",
                "filename": "\tcmd.pdf",
                "path": str(self.downloads / "cmd.pdf"),
                "sender": "\rreturn_payload",
                "subject": "Harmless Subject",
            },
        ]

        csv_target = self.base_dir / "sanitized.csv"
        count = cli.export_documents_to_csv(malicious_docs, csv_target)
        self.assertEqual(count, 2)

        with open(csv_target, "r", encoding="utf-8-sig", newline="") as f:
            reader = list(csv.reader(f, delimiter=";"))

        # Header check
        self.assertEqual(reader[0], ["Datum", "Profil", "Kategorie", "Dateiname", "Pfad", "Absender", "Betreff"])

        # Row 1 checks
        row1 = reader[1]
        self.assertTrue(row1[1].startswith("'="), f"Profile was not escaped: {row1[1]}")
        self.assertTrue(row1[3].startswith("'+"), f"Filename was not escaped: {row1[3]}")
        self.assertTrue(row1[5].startswith("'@"), f"Sender was not escaped: {row1[5]}")
        self.assertTrue(row1[6].startswith("'-"), f"Subject was not escaped: {row1[6]}")

        # Row 2 checks
        row2 = reader[2]
        self.assertTrue(row2[1].startswith("'"), f"Spaced formula was not escaped: {row2[1]}")
        self.assertTrue(row2[3].startswith("'\t"), f"Tab-leading filename was not escaped: {row2[3]}")
        self.assertTrue(row2[5].startswith("'\r"), f"Carriage return sender was not escaped: {row2[5]}")
        self.assertEqual(row2[6], "Harmless Subject")

    def test_csv_and_library_export_with_dataclass_objects(self):
        """Facet 4: Both CSV export and library export must support Document and SearchProfile objects without AttributeError."""
        doc_obj = Document(
            profile="Finanzen",
            filename="Quartalsbericht.pdf",
            date="2026-10-30",
            path=str(self.downloads / "Finanzen" / "Quartalsbericht.pdf"),
            sender="cfo@company.org",
            subject="Q3 Abschluss",
        )
        profile_obj = SearchProfile(
            id="p-obj-1",
            name="Finanzen",
            group="Finance",
            account_name="MainAccount",
            target_folder="Finanzen",
            active=True,
            override_settings=DownloadSettings(download_attachments=True),
        )
        account_obj = MailAccount(
            name="MainAccount",
            host="mail.example.com",
            user="user@example.com",
        )

        csv_target = self.base_dir / "object_export.csv"
        # CSV Export with dataclass instances
        count = cli.export_documents_to_csv([doc_obj], csv_target, profiles=[profile_obj])
        self.assertEqual(count, 1)
        csv_content = csv_target.read_text(encoding="utf-8-sig")
        self.assertIn("Quartalsbericht.pdf", csv_content)
        self.assertIn("Finanzen", csv_content)
        self.assertIn("cfo@company.org", csv_content)

        # Library export payload with dataclass instances
        payload = cli.build_library_export_payload(
            base_path_str=str(self.downloads),
            global_settings=DownloadSettings(),
            profiles=[profile_obj],
            accounts=[account_obj],
            scheduler_interval=30,
            documents=[doc_obj],
        )
        self.assertEqual(payload["schema"], "docsgrabber-library-v1")
        self.assertEqual(len(payload["profiles"]), 1)
        self.assertEqual(payload["profiles"][0]["name"], "Finanzen")
        self.assertEqual(len(payload["documents"]), 1)
        self.assertEqual(payload["documents"][0]["filename"], "Quartalsbericht.pdf")

    def test_cli_directory_resolution_non_existent_folder(self):
        """Facet 5: Non-existent destination directories and trailing slashes must resolve to default filenames inside that directory."""
        new_lib_dir = self.base_dir / "fresh_lib_dir"
        self.assertFalse(new_lib_dir.exists())

        exit_code = cli.run_cli([
            "--export-library", str(new_lib_dir),
            "--config", str(self.config_file),
            "--documents-db", str(self.docs_db),
        ])
        self.assertEqual(exit_code, 0)
        expected_json = new_lib_dir / "docsgrabber-library-v1.json"
        self.assertTrue(new_lib_dir.is_dir())
        self.assertTrue(expected_json.exists())

        new_csv_dir = self.base_dir / "fresh_csv_dir"
        self.assertFalse(new_csv_dir.exists())

        exit_code_csv = cli.run_cli([
            "--export-csv", str(new_csv_dir),
            "--config", str(self.config_file),
            "--documents-db", str(self.docs_db),
        ])
        self.assertEqual(exit_code_csv, 0)
        expected_csv = new_csv_dir / "documents_export.csv"
        self.assertTrue(new_csv_dir.is_dir())
        self.assertTrue(expected_csv.exists())


if __name__ == "__main__":
    unittest.main()
