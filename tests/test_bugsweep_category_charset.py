"""Regression tests for Bugsweep iteration: category inference & charset decoding hardening."""

import email.message
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock

import UniversalDocsGrabberV1 as app


def test_infer_document_category_root_profile_returns_empty():
    """Dokumente direkt im Profil-Ordner haben keine Kategorie."""
    base = Path("C:/UnivDocs")
    doc_path = "C:/UnivDocs/Invoices/rechnung_2026.pdf"
    assert app.infer_document_category(doc_path, base, "Invoices") == ""


def test_infer_document_category_subfolder_returns_category():
    """Dokumente in einem Unterordner des Profils haben diesen Unterordner als Kategorie."""
    base = Path("C:/UnivDocs")
    doc_path = "C:/UnivDocs/Invoices/Rechnungen/rechnung_2026.pdf"
    assert app.infer_document_category(doc_path, base, "Invoices") == "Rechnungen"


def test_infer_document_category_custom_target_folder():
    """Berücksichtigt benutzerdefinierte Zielordner."""
    base = Path("C:/UnivDocs")
    root_doc = "C:/UnivDocs/CustomTarget/doc.pdf"
    assert app.infer_document_category(root_doc, base, "ProfileName", "CustomTarget") == ""

    cat_doc = "C:/UnivDocs/CustomTarget/Steuer/doc.pdf"
    assert app.infer_document_category(cat_doc, base, "ProfileName", "CustomTarget") == "Steuer"


def test_infer_document_category_outside_base_returns_empty():
    """Dokumente außerhalb der base_path liefern leeren String."""
    base = Path("C:/UnivDocs")
    doc_path = "D:/OtherPlace/doc.pdf"
    assert app.infer_document_category(doc_path, base, "Invoices") == ""


def test_collect_category_entries_ignores_profile_root_files(tmp_path):
    """Profile selbst dürfen nicht als Scheinkategorien in die Export-Kategorien wandern."""
    base = tmp_path / "UnivDocs"
    profile = app.SearchProfile(id="p1", name="Invoices", group="Default", account_name="Acc1")
    doc = app.Document(
        profile="Invoices",
        filename="doc.pdf",
        date="2026-09-14",
        path=str(base / "Invoices" / "doc.pdf"),
    )
    categories = app.collect_category_entries(
        app.DownloadSettings(),
        [profile],
        [doc],
        base,
    )
    assert not any(c["name"] == "Invoices" for c in categories)
    assert len(categories) == 0


def test_build_library_export_payload_sets_none_category_for_root_files(tmp_path):
    """Unkategorisierte Dokumente im Profilordner haben category=None im Web-Export."""
    base = tmp_path / "UnivDocs"
    p_dir = base / "Invoices"
    p_dir.mkdir(parents=True)
    doc_file = p_dir / "doc.pdf"
    doc_file.write_bytes(b"pdf-content")

    profiles = [app.SearchProfile(id="p1", name="Invoices", group="Default", account_name="Acc1")]
    accounts = [app.MailAccount(name="Acc1", host="imap.example.com", user="user@example.com")]
    documents = [
        app.Document(
            profile="Invoices",
            filename="doc.pdf",
            date="2026-09-14",
            path=str(doc_file),
        )
    ]

    payload = app.build_library_export_payload(
        profiles,
        accounts,
        documents,
        app.DownloadSettings(),
        base,
        exported_at=datetime(2026, 9, 14, 12, 0, tzinfo=timezone.utc),
    )

    assert payload["documents"][0]["category"] is None
    assert not any(c["name"] == "Invoices" for c in payload["categories"])


def test_safe_decode_payload_handles_unknown_charset():
    """Unbekannte oder ungültige Charsets werfen keinen LookupError sondern nutzen Fallback."""
    raw = "Ärgerliche Rechnung".encode("utf-8")
    decoded = app.safe_decode_payload(raw, "unknown-8bit")
    assert "Rechnung" in decoded
    assert app.safe_decode_payload(None) == ""


def test_safe_decode_payload_handles_malformed_charset_spec():
    """Ungültige Charset-Spezifikationen mit Sonderzeichen werfen keinen LookupError."""
    raw = b"Hello World"
    decoded = app.safe_decode_payload(raw, "iso-8859-1; format=flowed")
    assert decoded == "Hello World"


def test_convert_body_to_pdf_with_unknown_charset(tmp_path):
    """_convert_body_to_pdf fängt ungültige Charsets ab und erzeugt Body ohne Mail Parse Error."""
    worker = app.GrabberWorker([], [], [], tmp_path, app.DownloadSettings())
    worker.log = MagicMock()
    worker.add_db = MagicMock()

    msg = email.message.EmailMessage()
    msg.set_payload("Rechnungstext ohne Anhang")
    del msg["Content-Type"]
    msg["Content-Type"] = "text/plain; charset=\"unknown-custom-codec\""

    out_dir = tmp_path / "Invoices"
    out_dir.mkdir()

    result = worker._convert_body_to_pdf(
        msg,
        "2026-09-14__Test__Rechnung",
        out_dir,
        "Invoices",
        "2026-09-14",
        "billing@example.com",
        "Rechnung",
    )
    assert result is True or result is None
