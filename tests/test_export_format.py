"""Tests for the redacted cross-platform export."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import UniversalDocsGrabberV1 as app


def test_build_library_export_payload_redacts_sensitive_fields(tmp_path):
    base_path = tmp_path / "UnivDocs"
    profile_dir = base_path / "Invoices" / "Rechnungen"
    profile_dir.mkdir(parents=True)
    inside_file = profile_dir / "rechnung.pdf"
    inside_file.write_bytes(b"sample-pdf")

    outside_file = tmp_path / "private" / "secret.pdf"
    outside_file.parent.mkdir()
    outside_file.write_bytes(b"secret-pdf")

    profiles = [
        app.SearchProfile(
            "profile-1",
            "Invoices",
            "Mail",
            "Primary Inbox",
            query_subject="Invoice",
            query_sender="billing@example.org",
            query_since="2026-05-01",
            gmail_query="has:attachment label:finance",
            override_settings=app.DownloadSettings(
                auto_categorize=True,
                category_rules=[{"keyword": "invoice", "folder": "Rechnungen"}],
            ),
        )
    ]
    accounts = [
        app.MailAccount(
            "Primary Inbox",
            "imap.example.org",
            "owner@example.org",
        )
    ]
    documents = [
        app.Document(
            "Invoices",
            "rechnung.pdf",
            "2026-05-08",
            str(inside_file),
            sender="billing@example.org",
            subject="Invoice 0815",
        ),
        app.Document(
            "Invoices",
            "secret.pdf",
            "2026-05-09",
            str(outside_file),
            sender="ceo@example.org",
            subject="Top secret",
        ),
    ]

    payload = app.build_library_export_payload(
        profiles,
        accounts,
        documents,
        app.DownloadSettings(category_rules=[{"keyword": "tax", "folder": "Steuer"}]),
        base_path,
        scheduler_interval=60,
        exported_at=datetime(2026, 5, 27, 10, 0, tzinfo=timezone.utc),
    )

    serialized = json.dumps(payload, ensure_ascii=False)

    assert payload["schema"] == "docsgrabber-library"
    assert payload["schema_version"] == "1.0"
    assert payload["app"]["exported_at"] == "2026-05-27T10:00:00+00:00"
    assert payload["accounts"][0]["ref"].startswith("account-")
    assert "owner@example.org" not in serialized
    assert str(base_path) not in serialized
    assert "billing@example.org" not in json.dumps(payload["documents"], ensure_ascii=False)
    assert "Invoice 0815" not in json.dumps(payload["documents"], ensure_ascii=False)
    assert payload["documents"][0]["path_hint"] == {
        "kind": "relative",
        "value": "Invoices/Rechnungen/rechnung.pdf",
    }
    assert payload["documents"][0]["category"] == "Rechnungen"
    assert payload["documents"][0]["status"] == "available"
    assert payload["documents"][0]["sha256"] is not None
    assert payload["documents"][1]["path_hint"] == {
        "kind": "basename",
        "value": "secret.pdf",
    }
    assert payload["run_summary"]["scheduler_interval_minutes"] == 60
    assert payload["run_summary"]["exported_document_count"] == 2
    assert sorted(category["name"] for category in payload["categories"]) == ["Rechnungen", "Steuer"]


def test_write_library_export_uses_utf8_without_bom(tmp_path):
    output_path = tmp_path / "docsgrabber-library-v1.json"
    payload = {
        "schema": "docsgrabber-library",
        "schema_version": "1.0",
        "categories": [{"name": "Überfällig"}],
    }

    app.write_library_export(output_path, payload)

    raw = output_path.read_bytes()
    assert not raw.startswith(b"\xef\xbb\xbf")
    text = output_path.read_text(encoding="utf-8")
    assert "Überfällig" in text
