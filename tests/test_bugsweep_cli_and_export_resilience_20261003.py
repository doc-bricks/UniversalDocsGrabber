"""Hermetic regression tests for CLI pipeline, export resilience, and DOS device sanitization."""

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


class TestBugsweepCliAndExportResilience(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp(prefix="udg_bugsweep_test_")
        self.dir_path = Path(self.temp_dir)
        self.config_path = self.dir_path / "config_v1.json"
        self.db_path = self.dir_path / "documents.json"
        self.download_path = self.dir_path / "Downloads"
        self.download_path.mkdir(parents=True, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_build_account_ref_fallbacks(self):
        for fn in (cli.build_account_ref, udg.build_account_ref):
            self.assertEqual(fn(""), "account-unknown")
            self.assertEqual(fn(None), "account-unknown")
            self.assertEqual(fn("   "), "account-unknown")
            ref = fn("user@example.com")
            self.assertTrue(ref.startswith("account-"))
            self.assertNotEqual(ref, "account-unknown")
            self.assertEqual(len(ref), len("account-") + 12)

    def test_sanitize_filename_reserved_dos_devices_with_extensions(self):
        for fn in (cli.sanitize_filename, udg.sanitize_filename):
            self.assertEqual(fn("CON.pdf"), "file_CON.pdf")
            self.assertEqual(fn("con.txt"), "file_con.txt")
            self.assertEqual(fn("PRN.docx"), "file_PRN.docx")
            self.assertEqual(fn("aux.jpg"), "file_aux.jpg")
            self.assertEqual(fn("NUL.dat"), "file_NUL.dat")
            self.assertEqual(fn("COM1.pdf"), "file_COM1.pdf")
            self.assertEqual(fn("lpt5.png"), "file_lpt5.png")
            self.assertEqual(fn("normal_report.pdf"), "normal_report.pdf")
            self.assertEqual(fn(""), "unnamed")
            self.assertEqual(fn(None), "unnamed")

    def test_infer_document_category_and_redact_path_hint_none_resilience(self):
        for module in (cli, udg):
            # None / empty path should never raise TypeError
            cat = module.infer_document_category(None, self.download_path, "Profile1", "Target")
            self.assertEqual(cat, "")
            cat_empty = module.infer_document_category("", self.download_path, "Profile1", "Target")
            self.assertEqual(cat_empty, "")

            hint_none = module.redact_path_hint(None, self.download_path)
            self.assertEqual(hint_none, {"kind": "basename", "value": ""})
            hint_empty = module.redact_path_hint("", self.download_path)
            self.assertEqual(hint_empty, {"kind": "basename", "value": ""})

    def test_build_library_export_payload_with_null_document_fields(self):
        sample_docs = [
            {
                "profile": None,
                "filename": None,
                "date": None,
                "path": None,
                "sender": None,
                "subject": None,
            },
            {
                "profile": "Invoices",
                "filename": "inv.pdf",
                "date": "2026-03-01",
                "path": str(self.download_path / "Invoices" / "inv.pdf"),
            },
        ]
        payload = cli.build_library_export_payload(
            base_path_str=str(self.download_path),
            global_settings={},
            profiles=[{"name": "Invoices", "active": True}],
            accounts=[{"name": "MainAcc"}],
            scheduler_interval=15,
            documents=sample_docs,
        )
        self.assertEqual(payload["schema"], "docsgrabber-library-v1")
        self.assertEqual(len(payload["documents"]), 2)
        doc0 = payload["documents"][0]
        self.assertEqual(doc0["profile_name"], "")
        self.assertEqual(doc0["status"], "missing")
        self.assertIsNone(doc0["sha256"])
        self.assertEqual(doc0["path_hint"], {"kind": "basename", "value": ""})

    def test_export_documents_to_csv_directory_target_and_none_fields(self):
        docs = [
            {"profile": None, "path": None, "date": None, "filename": "doc1.pdf", "sender": None, "subject": None},
            {"profile": "Rechnungen", "path": str(self.download_path / "a.pdf"), "date": "2026-05-01", "filename": "a.pdf", "sender": "x@y.de", "subject": "Rechnung"},
        ]
        # Target is a directory -> should create documents_export.csv inside it
        target_dir = self.dir_path / "csv_out_dir"
        target_dir.mkdir(parents=True, exist_ok=True)

        count = cli.export_documents_to_csv(
            documents=docs,
            output_path=target_dir,
            base_path_str=str(self.download_path),
        )
        self.assertEqual(count, 2)
        exported_csv = target_dir / "documents_export.csv"
        self.assertTrue(exported_csv.exists())

        with open(exported_csv, "r", encoding="utf-8-sig") as f:
            rows = list(csv.reader(f, delimiter=";"))
            self.assertEqual(len(rows), 3)  # header + 2 rows
            self.assertEqual(rows[0], ["Datum", "Profil", "Kategorie", "Dateiname", "Pfad", "Absender", "Betreff"])
            # row 1: None fields should be empty strings, not "None"
            self.assertEqual(rows[1][0], "")
            self.assertEqual(rows[1][1], "")
            self.assertEqual(rows[1][3], "doc1.pdf")
            self.assertEqual(rows[1][4], "")
            self.assertEqual(rows[1][5], "")
            self.assertEqual(rows[1][6], "")

    def test_cli_list_documents_with_profile_none_filter(self):
        config_data = {
            "base_path": str(self.download_path),
            "profiles": [{"name": "Steuern", "active": True}],
        }
        self.config_path.write_text(json.dumps(config_data), encoding="utf-8")
        docs_data = [
            {"profile": None, "filename": "unassigned.pdf", "date": "2026-01-01"},
            {"profile": "Steuern", "filename": "steuer_2026.pdf", "date": "2026-02-01"},
        ]
        self.db_path.write_text(json.dumps(docs_data), encoding="utf-8")

        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--list-documents",
                "--profile", "Steuern",
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        res = json.loads(out.getvalue())
        self.assertEqual(res["total_count"], 1)
        self.assertEqual(res["documents"][0]["filename"], "steuer_2026.pdf")

    def test_cli_export_library_directory_resolution_and_atomic_replace(self):
        config_data = {"base_path": str(self.download_path), "profiles": []}
        self.config_path.write_text(json.dumps(config_data), encoding="utf-8")
        self.db_path.write_text("[]", encoding="utf-8")

        target_dir = self.dir_path / "library_out_dir"
        target_dir.mkdir(parents=True, exist_ok=True)

        out = io.StringIO()
        with patch("sys.stdout", out):
            code = cli.run_cli([
                "--export-library", str(target_dir),
                "--json",
                "--config", str(self.config_path),
                "--documents-db", str(self.db_path),
            ])
        self.assertEqual(code, 0)
        expected_file = target_dir / "docsgrabber-library-v1.json"
        self.assertTrue(expected_file.exists())
        payload = json.loads(expected_file.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema"], "docsgrabber-library-v1")

    def test_load_data_none_and_corrupt_fields(self):
        corrupt_config = {
            "base_path": None,
            "scheduler_interval": None,
            "profiles": "not-a-list",
            "accounts": None,
        }
        self.config_path.write_text(json.dumps(corrupt_config), encoding="utf-8")
        base_path, settings, profiles, accounts, interval, docs = cli.load_data(
            config_path=str(self.config_path),
            db_path=str(self.db_path),
        )
        self.assertEqual(base_path, str(Path.home() / "Downloads" / "UnivDocs"))
        self.assertEqual(interval, 0)
        self.assertEqual(profiles, [])
        self.assertEqual(accounts, [])

    def test_check_system_stack_cleans_up_test_file(self):
        report = cli.check_system_stack(base_path_str=str(self.download_path))
        self.assertIn("storage", report["components"])
        self.assertTrue(report["components"]["storage"]["writable"])
        # Ensure no .write_test_...tmp file was left behind
        tmp_files = list(self.download_path.glob(".write_test_*.tmp"))
        self.assertEqual(len(tmp_files), 0)

    def test_udg_write_library_export_directory_and_atomic(self):
        target_dir = self.dir_path / "udg_lib_dir"
        target_dir.mkdir(parents=True, exist_ok=True)
        payload = {"test": 123}
        udg.write_library_export(target_dir, payload)
        expected_file = target_dir / "docsgrabber-library-v1.json"
        self.assertTrue(expected_file.exists())
        self.assertEqual(json.loads(expected_file.read_text(encoding="utf-8")), payload)


if __name__ == "__main__":
    unittest.main()
