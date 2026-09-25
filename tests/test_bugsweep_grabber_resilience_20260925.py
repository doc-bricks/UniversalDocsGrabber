"""Regression tests for SOFTWARE-BUGSEARCH 2026-09-25: Grabber Resilience, Metadata, Query-Builder & Deduplication."""

import email.message
import email.utils
from pathlib import Path
from types import SimpleNamespace

import UniversalDocsGrabberV1 as app


def test_query_builder_comma_separated_phrases():
    """Multi-word phrases separated by comma must not be split into separate words."""
    res = app.QueryBuilderDialog._parse_comma_separated_input("from", "Telekom Deutschland, Allianz Global")
    assert res == 'from:("Telekom Deutschland" OR "Allianz Global")'

    res_single = app.QueryBuilderDialog._parse_comma_separated_input("from", "Telekom Deutschland")
    assert res_single == 'from:"Telekom Deutschland"'

    res_quoted = app.QueryBuilderDialog._parse_comma_separated_input("subject", '"Rechnung 2026", Mahnung')
    assert res_quoted == 'subject:("Rechnung 2026" OR Mahnung)'


def test_parse_email_metadata_sender_bracket_only():
    """From-Header ohne Display-Namen ('<service@paypal.de>') muss die Adresse erhalten und nicht leer sein."""
    msg = email.message.EmailMessage()
    msg["From"] = "<service@paypal.de>"
    msg["Subject"] = "Zahlungsbestätigung"
    msg["Date"] = "Mon, 25 Sep 2026 12:00:00 +0200"

    worker = app.GrabberWorker([], [], app.DownloadSettings(), Path("."), [])
    sender, subject, date_iso = worker._parse_email_metadata(msg)

    assert sender == "service@paypal.de"
    assert subject == "Zahlungsbestätigung"
    assert date_iso == "2026-09-25"


def test_parse_email_metadata_pre1970_or_invalid_date_windows():
    """Historische oder pre-1970 Zeitstempel dürfen auf Windows nicht mit OSError abstürzen."""
    msg = email.message.EmailMessage()
    msg["From"] = "John Doe <john@example.com>"
    msg["Subject"] = "Historic Doc"
    msg["Date"] = "Sun, 01 Jan 1960 00:00:00 +0000"

    worker = app.GrabberWorker([], [], app.DownloadSettings(), Path("."), [])
    sender, subject, date_iso = worker._parse_email_metadata(msg)

    assert sender == "John Doe"
    assert date_iso == "1960-01-01"


def test_auto_categorize_umlaut_kuendigung_and_vertraege():
    """Kategorisierung muss echte deutsche Umlaute für Kündigung und Verträge erkennen."""
    settings = app.DownloadSettings(auto_categorize=True)
    worker = app.GrabberWorker([], [], settings, Path("."), [])

    cat_kuendigung = worker._auto_categorize("Versicherung", "Kündigung zum nächstmöglichen Zeitpunkt", settings)
    assert cat_kuendigung == "Kündigungen"

    cat_vertraege = worker._auto_categorize("Kanzlei", "Verträge zur Durchsicht", settings)
    assert cat_vertraege == "Verträge"


def test_infer_document_category_foreign_subfolder_returns_empty():
    """Unterordner, die weder zum Profil noch zum Target-Folder gehören, dürfen keine Scheinkategorie liefern."""
    base = Path("C:/UnivDocs")
    foreign_doc = "C:/UnivDocs/ForeignFolder/Sub/doc.pdf"
    res = app.infer_document_category(foreign_doc, base, "MyProfile", "TargetFolder")
    assert res == ""


def test_convert_body_to_pdf_ignores_html_attachments(tmp_path, monkeypatch):
    """HTML-Anhänge dürfen nicht irrtümlich als E-Mail-Body verwendet werden."""
    msg = email.message.EmailMessage()
    msg["Subject"] = "Test Mail"
    msg["From"] = "sender@example.com"
    msg.set_content("Dies ist der eigentliche Text-Body der E-Mail.")
    msg.add_attachment(b"<html><body>Attached HTML Document</body></html>",
                       maintype="text", subtype="html", filename="attached_report.html")

    captured_html = []
    def fake_create_pdf(src, dest):
        captured_html.append(src)
        dest.write(b"%PDF-1.4 Fake PDF")
        return SimpleNamespace(err=0)

    monkeypatch.setattr(app, "pisa", SimpleNamespace(CreatePDF=fake_create_pdf))
    monkeypatch.setattr(app, "PISA_AVAILABLE", True)

    worker = app.GrabberWorker([], [], app.DownloadSettings(), tmp_path, [])
    worker._convert_body_to_pdf(msg, "test_base", tmp_path, "Prof", "2026-09-25", "sender@example.com", "Test Mail")

    assert len(captured_html) == 1
    # Der Body muss den Plain-Text-Inhalt (<pre>) enthalten und NICHT den HTML-Anhang
    assert "Dies ist der eigentliche Text-Body" in captured_html[0]
    assert "Attached HTML Document" not in captured_html[0]


def test_convert_body_to_pdf_exception_cleans_up_target(tmp_path, monkeypatch):
    """Unerwartete Exceptions in pisa.CreatePDF müssen gefangen und 0-Byte-Zieldateien bereinigt werden."""
    msg = email.message.EmailMessage()
    msg.set_content("Mail text")

    def broken_create_pdf(src, dest):
        dest.write(b"corrupt")
        raise AttributeError("Simulated internal xhtml2pdf crash")

    monkeypatch.setattr(app, "pisa", SimpleNamespace(CreatePDF=broken_create_pdf))
    monkeypatch.setattr(app, "PISA_AVAILABLE", True)

    worker = app.GrabberWorker([], [], app.DownloadSettings(), tmp_path, [])
    worker._convert_body_to_pdf(msg, "crash_base", tmp_path, "Prof", "2026-09-25", "sender", "subj")

    target = tmp_path / "crash_base_MAIL.pdf"
    assert not target.exists()


def test_build_imap_search_args_whitespace_query_safeguard():
    """Whitespace-only Suchfilter dürfen keine Wildcard-Abfragen (FROM '') erzeugen und Newlines müssen bereinigt werden."""
    prof = app.SearchProfile(
        id="p1",
        name="Test",
        group="G",
        account_name="Acc",
        query_sender="   ",
        query_subject="Rechnung\r\nInjected",
    )
    worker = app.GrabberWorker([], [], app.DownloadSettings(), Path("."), [])
    args = worker.build_imap_search_args(prof)

    assert "FROM" not in args
    assert "SUBJECT" in args
    idx = args.index("SUBJECT")
    subj_val = args[idx + 1]
    assert "\r" not in subj_val and "\n" not in subj_val
    assert subj_val == '"Rechnung Injected"'


def test_run_deduplication_ignores_directories_and_updates_db(tmp_path):
    """run_deduplication ignoriert Ordner mit Punkten im Namen und entfernt gelöschte Dateien aus der DB."""
    # Ordner mit Punkt im Namen erstellen
    dotted_dir = tmp_path / "Subfolder_1.0"
    dotted_dir.mkdir()
    (dotted_dir / "keep.pdf").write_bytes(b"unique content")

    # Zwei identische Dateien
    file1 = tmp_path / "doc1.pdf"
    file2 = tmp_path / "doc2.pdf"
    file1.write_bytes(b"same content")
    file2.write_bytes(b"same content")

    db = [
        app.Document(profile="P", filename="doc1.pdf", date="2026-09-25", path=str(file1)),
        app.Document(profile="P", filename="doc2.pdf", date="2026-09-25", path=str(file2)),
        app.Document(profile="P", filename="keep.pdf", date="2026-09-25", path=str(dotted_dir / "keep.pdf")),
    ]

    settings = app.DownloadSettings(enable_hash_check=True)
    worker = app.GrabberWorker([], [], settings, tmp_path, db)

    worker.run_deduplication()

    # Genau eine der beiden Duplikat-Dateien existiert noch
    remaining_files = [f for f in [file1, file2] if f.exists()]
    assert len(remaining_files) == 1

    # Die DB darf nur noch die existierenden Dateien referenzieren
    assert len(db) == 2
    assert all(Path(d.path).exists() for d in db)
