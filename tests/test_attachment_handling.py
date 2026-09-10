"""
Tests für robuste Anhangsverarbeitung in UniversalDocsGrabber.
Prüft Multi-Attachment-Szenarien, Kollisionsauflösung und Content-Disposition-Fallback.
"""

import email.message
from pathlib import Path
import UniversalDocsGrabberV1 as app


class DummyPart:
    """Mock-MIME-Part für Anhangstests."""

    def __init__(self, filename: str, payload: bytes = b"%PDF-1.4 dummy", content_type: str = "application/pdf", disposition: str = "attachment"):
        self._filename = filename
        self._payload = payload
        self._content_type = content_type
        self._disposition = disposition

    def get_filename(self):
        return self._filename

    def get_content_maintype(self):
        return self._content_type.split("/")[0]

    def get(self, header: str, default=None):
        if header.lower() == "content-disposition":
            return self._disposition
        return default

    def get_payload(self, decode: bool = False):
        return self._payload


def test_single_attachment_backward_compatibility(tmp_path: Path):
    """Einzelner Anhang erhält das klassische _ATT.<ext>-Muster."""
    worker = app.GrabberWorker([], [], app.DownloadSettings(), tmp_path, [])
    part = DummyPart("rechnung.pdf", b"%PDF-dummy")
    settings = app.DownloadSettings(download_attachments=True, formats=["pdf"])

    res = worker._save_attachment(
        part=part,
        base_name="2026-09-10__firma__rechnung",
        dl_dir=tmp_path,
        settings=settings,
        profile_name="TestProf",
        date_iso="2026-09-10",
        sender="firma@example.com",
        subject="Rechnung",
        attachment_index=1,
    )

    assert res is True
    expected_file = tmp_path / "2026-09-10__firma__rechnung_ATT.pdf"
    assert expected_file.exists()
    assert expected_file.read_bytes() == b"%PDF-dummy"
    assert len(worker.db) == 1
    assert worker.db[0].filename == expected_file.name


def test_multiple_attachments_saved_without_collision(tmp_path: Path):
    """Mehrere Anhänge mit gleicher Dateiendung werden beide gespeichert und nicht überschrieben/verworfen."""
    worker = app.GrabberWorker([], [], app.DownloadSettings(), tmp_path, [])
    part1 = DummyPart("rechnung_seite1.pdf", b"%PDF-part1")
    part2 = DummyPart("rechnung_seite2.pdf", b"%PDF-part2")
    part3 = DummyPart("anhang.pdf", b"%PDF-part3")
    settings = app.DownloadSettings(download_attachments=True, formats=["pdf"])

    res1 = worker._save_attachment(
        part=part1,
        base_name="2026-09-10__firma__rechnung",
        dl_dir=tmp_path,
        settings=settings,
        profile_name="TestProf",
        date_iso="2026-09-10",
        sender="firma@example.com",
        subject="Rechnung",
        attachment_index=1,
    )
    res2 = worker._save_attachment(
        part=part2,
        base_name="2026-09-10__firma__rechnung",
        dl_dir=tmp_path,
        settings=settings,
        profile_name="TestProf",
        date_iso="2026-09-10",
        sender="firma@example.com",
        subject="Rechnung",
        attachment_index=2,
    )
    res3 = worker._save_attachment(
        part=part3,
        base_name="2026-09-10__firma__rechnung",
        dl_dir=tmp_path,
        settings=settings,
        profile_name="TestProf",
        date_iso="2026-09-10",
        sender="firma@example.com",
        subject="Rechnung",
        attachment_index=3,
    )

    assert res1 is True
    assert res2 is True
    assert res3 is True

    files = sorted([f.name for f in tmp_path.glob("*.pdf")])
    assert len(files) == 3
    # Erster Anhang behält _ATT.pdf
    assert "2026-09-10__firma__rechnung_ATT.pdf" in files
    # Zweiter und dritter Anhang erhalten ihren Index
    assert any("ATT_2" in fn for fn in files)
    assert any("ATT_3" in fn for fn in files)
    assert len(worker.db) == 3


def test_attachment_without_content_disposition_recognized(tmp_path: Path):
    """Anhänge ohne Content-Disposition-Header werden zuverlässig extrahiert."""
    worker = app.GrabberWorker([], [], app.DownloadSettings(), tmp_path, [])
    # Erstelle eine simulierte Multipart-E-Mail
    msg = email.message.EmailMessage()
    msg["From"] = "sender@example.com"
    msg["Subject"] = "Dokumente"
    msg["Date"] = "Wed, 10 Sep 2026 10:00:00 +0200"

    # Teil 1: HTML-Text
    msg.add_header("Content-Type", "multipart/mixed")
    html_part = email.message.EmailMessage()
    html_part.set_content("<p>Hier ist die Datei</p>", subtype="html")
    msg.attach(html_part)

    # Teil 2: Anhang OHNE Content-Disposition, aber mit Content-Type-Name
    att_part = email.message.EmailMessage()
    att_part.set_type("application/pdf")
    att_part.set_param("name", "scan_bericht.pdf")
    att_part.set_payload(b"%PDF-scan")
    # Stelle sicher, dass kein Content-Disposition Header existiert
    if "Content-Disposition" in att_part:
        del att_part["Content-Disposition"]
    msg.attach(att_part)

    class MockConn:
        def uid(self, action, num, *args):
            return "OK", [(b"1", msg.as_bytes())]

    settings = app.DownloadSettings(download_attachments=True, convert_body_to_pdf=False, formats=["pdf"])
    worker.process_email(MockConn(), b"123", tmp_path, settings, "ScanProfil")

    saved_files = list(tmp_path.glob("*.pdf"))
    assert len(saved_files) == 1
    assert b"%PDF-scan" in saved_files[0].read_bytes()
