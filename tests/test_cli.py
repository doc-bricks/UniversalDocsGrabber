"""Unit and integration tests for UniversalDocsGrabber headless CLI interface."""

from __future__ import annotations

import csv
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import cli
import UniversalDocsGrabberV1 as udg


class TestUniversalDocsGrabberCLI(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="udg_cli_test_")
        self.dir_path = Path(self.temp_dir)
        self.config_path = self.dir_path / "config_v1.json"
        self.db_path = self.dir_path / "documents.json"
        self.base_download_path = self.dir_path / "Downloads"
        self.base_download_path.mkdir(parents=True, exist_ok=True)

        # Mock sample config
        self.sample_config = {
            "base_path": str(self.base_download_path),
            "scheduler_interval": 30,
            "global_settings": {
                "download_attachments": True,
                "convert_body_to_pdf": True,
                "convert_all_to_pdf": False,
                "enable_hash_check": True,
                "auto_categorize": True,
                "category_rules": [
                    {"keyword": "rechnung", "folder": "Rechnungen", "match": "contains"},
                    {"keyword": "vertrag", "folder": "Vertraege", "match": "contains"},
                ],
                "formats": ["pdf", "docx", "png"],
            },
            "accounts": [
                {
                    "name": "Haupt-GMX",
                    "host": "imap.gmx.net",
                    "user": "max@example.com",
                    "port": 993,
                    "search_folder": "INBOX",
                    "password": "SUPER_SECRET_PLAINTEXT_PW",
                }
            ],
            "profiles": [
                {
                    "id": "prof-101",
                    "name": "Rechnungen 2026",
                    "group": "Finanzen",
                    "account_name": "Haupt-GMX",
                    "query_subject": "Rechnung",
                    "query_sender": "",
                    "query_since": "2026-01-01",
                    "target_folder": "Rechnungen",
                    "active": True,
                    "gmail_query": "has:attachment filename:pdf",
                },
                {
                    "id": "prof-102",
                    "name": "Vertraege Archiv",
                    "group": "Recht",
                    "account_name": "Haupt-GMX",
                    "query_subject": "Vertrag",
                    "query_sender": "",
                    "query_since": "",
                    "target_folder": "Vertraege",
                    "active": False,
                    "gmail_query": "",
                },
            ],
        }
        self.config_path.write_text(json.dumps(self.sample_config, indent=2), encoding="utf-8")

        # Mock sample documents
        doc1_dir = self.base_download_path / "Rechnungen" / "Rechnungen"
        doc1_dir.mkdir(parents=True, exist_ok=True)
        doc1_file = doc1_dir / "Rechnung_2026_01.pdf"
        doc1_file.write_bytes(b"%PDF-1.4 mock content for hash")

        doc2_dir = self.base_download_path / "Vertraege" / "Vertraege"
        doc2_dir.mkdir(parents=True, exist_ok=True)
        doc2_file = doc2_dir / "Vertrag_2026.docx"
        doc2_file.write_bytes(b"PK mock docx content")

        self.sample_docs = [
            {
                "profile": "Rechnungen 2026",
                "filename": "Rechnung_2026_01.pdf",
                "date": "2026-01-15",
                "path": str(doc1_file),
                "sender": "service@telekom.de",
                "subject": "Ihre Telekom Rechnung Januar 2026",
            },
            {
                "profile": "Vertraege Archiv",
                "filename": "Vertrag_2026.docx",
                "date": "2026-02-01",
                "path": str(doc2_file),
                "sender": "kontakt@anwalt.de",
                "subject": "Vertragsentwurf 2026",
            },
        ]
        self.db_path.write_text(json.dumps(self.sample_docs, indent=2), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_version_output(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            with self.assertRaises(SystemExit) as cm:
                cli.run_cli(["--version"])
            self.assertEqual(cm.exception.code, 0)
        self.assertIn("UniversalDocsGrabber 1.1.7", out.getvalue())

    def test_has_cli_action_detection(self):
        self.assertTrue(cli.has_cli_action(["--version"]))
        self.assertTrue(cli.has_cli_action(["-v"]))
        self.assertTrue(cli.has_cli_action(["--help"]))
        self.assertTrue(cli.has_cli_action(["-h"]))
        self.assertTrue(cli.has_cli_action(["--list-profiles"]))
        self.assertTrue(cli.has_cli_action(["--list-accounts"]))
        self.assertTrue(cli.has_cli_action(["--list-documents"]))
        self.assertTrue(cli.has_cli_action(["--export-library"]))
        self.assertTrue(cli.has_cli_action(["--export-csv"]))
        self.assertTrue(cli.has_cli_action(["--diagnose"]))
        self.assertTrue(cli.has_cli_action(["--check-stack"]))
        self.assertFalse(cli.has_cli_action([]))
        self.assertFalse(cli.has_cli_action(["--gui"]))
        self.assertFalse(cli.has_cli_action(["--json"]))

    def test_load_data_with_missing_files(self):
        non_existent_config = self.dir_path / "missing_config.json"
        non_existent_db = self.dir_path / "missing_db.json"

        base_path, settings, profiles, accounts, interval, docs = cli.load_data(
            config_path=str(non_existent_config),
            db_path=str(non_existent_db),
        )
        self.assertEqual(profiles, [])
        self.assertEqual(accounts, [])
        self.assertEqual(docs, [])
        self.assertEqual(interval, 0)
        self.assertTrue("download_attachments" in settings)

    def test_list_profiles_json(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-profiles",
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "Rechnungen 2026")
        self.assertEqual(data[0]["group"], "Finanzen")
        self.assertEqual(data[1]["name"], "Vertraege Archiv")
        self.assertFalse(data[1]["active"])

    def test_list_profiles_text(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-profiles",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("Konfigurierte Suchprofile (2):", text)
        self.assertIn("Rechnungen 2026", text)
        self.assertIn("Vertraege Archiv", text)
        self.assertIn("Aktiv", text)
        self.assertIn("Inaktiv", text)

    def test_list_accounts_masks_passwords(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-accounts",
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0]["name"], "Haupt-GMX")
        self.assertEqual(data[0]["user"], "max@example.com")
        self.assertEqual(data[0]["password"], "***MASKED***")
        self.assertNotIn("SUPER_SECRET_PLAINTEXT_PW", out.getvalue())

    def test_list_accounts_text(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-accounts",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        text = out.getvalue()
        self.assertIn("Konfigurierte E-Mail-Konten (1):", text)
        self.assertIn("Haupt-GMX", text)
        self.assertIn("max@example.com", text)
        self.assertNotIn("SUPER_SECRET_PLAINTEXT_PW", text)

    def test_list_documents_filtering_and_limit(self):
        # 1. Without filter
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-documents",
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(data["total_count"], 2)
        self.assertEqual(len(data["documents"]), 2)

        # 2. Filter by profile
        out_prof = io.StringIO()
        with patch("sys.stdout", out_prof):
            code = cli.run_cli([
                "--list-documents",
                "--profile", "Rechnungen 2026",
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data_prof = json.loads(out_prof.getvalue())
        self.assertEqual(data_prof["total_count"], 1)
        self.assertEqual(data_prof["documents"][0]["filename"], "Rechnung_2026_01.pdf")

        # 3. Limit
        out_lim = io.StringIO()
        with patch("sys.stdout", out_lim):
            code = cli.run_cli([
                "--list-documents",
                "--limit", "1",
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data_lim = json.loads(out_lim.getvalue())
        self.assertEqual(data_lim["total_count"], 2)
        self.assertEqual(len(data_lim["documents"]), 1)

    def test_export_library_json(self):
        export_file = self.dir_path / "companion_export.json"
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--export-library", str(export_file),
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        self.assertTrue(export_file.exists())

        payload = json.loads(export_file.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "docsgrabber-library-v1")
        self.assertEqual(payload["schema_version"], "1.0.0")
        self.assertEqual(payload["app"]["name"], "UniversalDocsGrabber")
        self.assertTrue(payload["capabilities"]["redacted"])
        self.assertFalse(payload["capabilities"]["contains_credentials"])
        self.assertNotIn("SUPER_SECRET_PLAINTEXT_PW", export_file.read_text(encoding="utf-8"))
        self.assertEqual(payload["run_summary"]["exported_profile_count"], 2)
        self.assertEqual(payload["run_summary"]["exported_document_count"], 2)

    def test_export_csv(self):
        csv_file = self.dir_path / "export.csv"
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--export-csv", str(csv_file),
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        self.assertTrue(csv_file.exists())

        # Verify CSV format and UTF-8 BOM
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = list(csv.reader(f, delimiter=";"))
            self.assertEqual(len(reader), 3)  # Header + 2 docs
            self.assertEqual(reader[0][0], "Datum")
            self.assertEqual(reader[0][1], "Profil")
            self.assertEqual(reader[0][3], "Dateiname")
            self.assertEqual(reader[1][1], "Rechnungen 2026")
            self.assertEqual(reader[1][3], "Rechnung_2026_01.pdf")
            self.assertEqual(reader[2][1], "Vertraege Archiv")
            self.assertEqual(reader[2][3], "Vertrag_2026.docx")

    def test_diagnose_stack(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--diagnose",
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertIn(code, (0, 1))
        report = json.loads(out.getvalue())
        self.assertEqual(report["app"], "UniversalDocsGrabber")
        self.assertIn("components", report)
        self.assertIn("pypdf", report["components"])
        self.assertIn("storage", report["components"])

    def test_gui_flag_returns_minus_one(self):
        code = cli.run_cli(["--gui"])
        self.assertEqual(code, -1)

    def test_main_delegates_to_cli(self):
        out = io.StringIO()
        with patch("sys.stdout", out):
            code = udg.main([
                "--list-profiles",
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        data = json.loads(out.getvalue())
        self.assertEqual(len(data), 2)


if __name__ == "__main__":
    unittest.main()
