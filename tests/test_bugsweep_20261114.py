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


class _AsciiImap:
    """Verhält sich bei str-Argumenten wie imaplib: kodiert mit ASCII, im UTF8=ACCEPT-Modus mit UTF-8.
    Treffer je Suchwert über `hits` (Suchwert -> UIDs), Literal wie imaplib über conn.literal."""

    def __init__(self, hits, utf8=False):
        self.hits = hits
        self.utf8_enabled = utf8
        self.literal = None
        self.capabilities = ()
        self.searches = []

    def uid(self, command, *args):
        encoding = "utf-8" if self.utf8_enabled else "ascii"
        for arg in args:
            if isinstance(arg, str):
                bytes(arg, encoding)  # wirft wie imaplib UnicodeEncodeError
        literal, self.literal = self.literal, None
        self.searches.append((args, literal))
        terms = [literal.decode("utf-8")] if literal is not None else []
        terms += [a.strip('"') for a in args if a.startswith('"')]
        matched = None
        for term in terms:
            uids = set(self.hits.get(term, []))
            matched = uids if matched is None else matched & uids
        return "OK", [b" ".join(sorted(matched or set(), key=int))]


def _run_profile(conn, sender="", subject="", tmp_path=None):
    profile = app.SearchProfile(id="p", name="Rechnungen", group="", account_name="a",
                                query_sender=sender, query_subject=subject)
    worker = app.GrabberWorker([profile], [], app.DownloadSettings(), tmp_path, [])
    logs, fetched = [], []
    worker.log.connect(logs.append)
    worker.process_email = lambda conn, num, dl_dir, settings, name: fetched.append(num)
    worker.process_profile(conn, profile, app.DownloadSettings())
    return logs, fetched


def test_imap_search_with_umlauts_works(tmp_path):
    """imaplib kodiert Suchargumente als ASCII: ein Profil mit Betreff „Kündigung“ oder Absender
    „Müller GmbH“ scheiterte komplett („Suchfehler: 'ascii' codec…“) und lud nichts."""
    conn = _AsciiImap({"Kündigung": [b"3", b"7"]})
    logs, fetched = _run_profile(conn, subject="Kündigung", tmp_path=tmp_path)
    assert not any("Suchfehler" in line for line in logs), logs
    assert fetched == [b"3", b"7"]
    args, literal = conn.searches[0]
    assert args[:2] == ("CHARSET", "UTF-8") and literal == "Kündigung".encode("utf-8")


def test_imap_search_with_two_umlaut_criteria_intersects(tmp_path):
    conn = _AsciiImap({"Müller GmbH": [b"1", b"2", b"5"], "Kündigung": [b"2", b"5", b"9"]})
    logs, fetched = _run_profile(conn, sender="Müller GmbH", subject="Kündigung", tmp_path=tmp_path)
    assert not any("Suchfehler" in line for line in logs), logs
    assert fetched == [b"2", b"5"]
    assert len(conn.searches) == 2  # imaplib sendet nur ein Literal pro Befehl


def test_imap_search_uses_plain_strings_in_utf8_mode_and_for_ascii(tmp_path):
    conn = _AsciiImap({"Kündigung": [b"4"]}, utf8=True)
    _, fetched = _run_profile(conn, subject="Kündigung", tmp_path=tmp_path)
    assert fetched == [b"4"] and conn.searches[0][1] is None and "CHARSET" not in conn.searches[0][0]
    conn = _AsciiImap({"Rechnung": [b"8"]})
    _, fetched = _run_profile(conn, subject="Rechnung", tmp_path=tmp_path)
    assert fetched == [b"8"] and conn.searches[0][0] == ("SUBJECT", '"Rechnung"')
