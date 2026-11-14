"""Regressionstests — Bugsweep UniversalDocsGrabber 2026-11-14."""
import email.message
from types import SimpleNamespace

import UniversalDocsGrabberV1 as app


def test_mail_body_pdf_name_is_capped_like_attachments(tmp_path, monkeypatch):
    """Anhänge kürzen den Basisnamen auf 120 Zeichen, das Mailtext-PDF nicht: bei langem Absender und
    Betreff (je bis 100 Zeichen) wurde der Pfad unter Windows (Standard: keine langen Pfade) über 260
    Zeichen lang — das PDF scheiterte und der Mailtext wurde nicht archiviert."""
    msg = email.message.EmailMessage()
    msg.set_content("Rechnung im Anhang.")

    def fake_create_pdf(src, dest):
        dest.write(b"%PDF-1.4 Fake")
        return SimpleNamespace(err=0)

    monkeypatch.setattr(app, "pisa", SimpleNamespace(CreatePDF=fake_create_pdf))
    monkeypatch.setattr(app, "PISA_AVAILABLE", True)
    base_name = f"2026-11-14__{'Absender_' * 11}__{'Betreff_' * 12}"
    assert len(base_name) > 200
    worker = app.GrabberWorker([], [], app.DownloadSettings(), tmp_path, [])
    worker._convert_body_to_pdf(msg, base_name, tmp_path, "Prof", "2026-11-14", "a", "b")
    created = [p.name for p in tmp_path.glob("*_MAIL.pdf")]
    assert len(created) == 1
    assert len(created[0]) <= len("_MAIL.pdf") + 120, created[0]
