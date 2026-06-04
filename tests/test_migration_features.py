"""Regression tests for migrated UniversalDocsGrabber features."""

import os
import sys
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace
from datetime import datetime

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication

import UniversalDocsGrabberV1 as app


def _make_message(subject="Test Subject", sender="Sender <sender@example.org>", body="Hello body"):
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = sender
    msg["Date"] = "Thu, 08 May 2026 10:00:00 +0000"
    msg.set_content(body)
    return msg


def test_process_email_falls_back_to_body_pdf_when_mail_has_no_attachments(tmp_path, monkeypatch):
    worker = app.GrabberWorker(
        [],
        [],
        app.DownloadSettings(convert_body_to_pdf=False),
        tmp_path,
        [],
    )
    msg = _make_message(body="Body only")
    calls = []

    class FakeConn:
        def fetch(self, _num, _spec):
            return "OK", [(None, msg.as_bytes())]

    def fake_convert(mail, base_name, dl_dir, profile_name, date_iso, sender, subject):
        calls.append(
            {
                "mail": mail,
                "base_name": base_name,
                "dl_dir": dl_dir,
                "profile_name": profile_name,
                "date_iso": date_iso,
                "sender": sender,
                "subject": subject,
            }
        )

    monkeypatch.setattr(worker, "_convert_body_to_pdf", fake_convert)

    worker.process_email(FakeConn(), b"1", tmp_path, worker.global_settings, "BodyProfile")

    assert len(calls) == 1
    assert calls[0]["profile_name"] == "BodyProfile"
    assert calls[0]["dl_dir"] == tmp_path
    assert calls[0]["subject"] == "Test Subject"


def test_convert_body_to_pdf_creates_pdf_and_document_entry(tmp_path, monkeypatch):
    documents = []
    worker = app.GrabberWorker(
        [],
        [],
        app.DownloadSettings(),
        tmp_path,
        documents,
    )
    msg = _make_message(body="Plain text with <angle brackets> & symbols")
    seen = {}

    def fake_create_pdf(content, dest):
        seen["content"] = content
        dest.write(b"%PDF-1.4 fake")
        return SimpleNamespace(err=0)

    monkeypatch.setattr(app, "pisa", SimpleNamespace(CreatePDF=fake_create_pdf))
    monkeypatch.setattr(app, "PISA_AVAILABLE", True)

    worker._convert_body_to_pdf(
        msg,
        "sample_mail",
        tmp_path,
        "Invoices",
        "2026-05-08",
        "Sender",
        "Test Subject",
    )

    pdf_path = tmp_path / "sample_mail_MAIL.pdf"
    assert pdf_path.exists()
    assert seen["content"].startswith("<pre>")
    assert "&lt;angle brackets&gt;" in seen["content"]
    assert "&amp;" in seen["content"]
    assert len(documents) == 1
    assert documents[0].filename == "sample_mail_MAIL.pdf"
    assert documents[0].profile == "Invoices"


def test_convert_body_to_pdf_cleans_up_on_pisa_error(tmp_path, monkeypatch):
    """Wenn pisa.CreatePDF einen Fehler meldet (err != 0), darf kein Dokument in die DB."""
    documents = []
    worker = app.GrabberWorker([], [], app.DownloadSettings(), tmp_path, documents)
    msg = _make_message(body="broken body")
    log_messages = []
    monkeypatch.setattr(worker, "log", SimpleNamespace(emit=log_messages.append))

    def fake_create_pdf_error(content, dest):
        return SimpleNamespace(err=1)

    monkeypatch.setattr(app, "pisa", SimpleNamespace(CreatePDF=fake_create_pdf_error))
    monkeypatch.setattr(app, "PISA_AVAILABLE", True)

    worker._convert_body_to_pdf(msg, "err_mail", tmp_path, "TestProfile", "2026-06-04", "S", "Sub")

    assert not (tmp_path / "err_mail_MAIL.pdf").exists()
    assert len(documents) == 0
    assert any("fehlgeschlagen" in m or "err=" in m for m in log_messages)


def test_convert_body_to_pdf_skips_gracefully_when_pisa_unavailable(tmp_path, monkeypatch):
    """Ohne xhtml2pdf (PISA_AVAILABLE=False) muss _convert_body_to_pdf ohne NameError abbrechen."""
    documents = []
    worker = app.GrabberWorker([], [], app.DownloadSettings(), tmp_path, documents)
    msg = _make_message(body="Should not be converted")
    monkeypatch.setattr(app, "PISA_AVAILABLE", False)
    log_messages = []
    monkeypatch.setattr(worker, "log", SimpleNamespace(emit=log_messages.append))

    worker._convert_body_to_pdf(msg, "no_pisa", tmp_path, "TestProfile", "2026-06-04", "S", "Sub")

    assert not (tmp_path / "no_pisa_MAIL.pdf").exists()
    assert len(documents) == 0
    assert any("xhtml2pdf" in m or "fehlt" in m for m in log_messages)


def test_sync_profile_order_updates_order_and_group(tmp_path, monkeypatch):
    qapp = QApplication.instance() or QApplication(sys.argv)
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "config_v1.json")
    monkeypatch.setattr(app, "DOCS_DB", tmp_path / "documents.json")

    window = app.MainWindow()
    first = app.SearchProfile("1", "First", "Group A", "acc1")
    second = app.SearchProfile("2", "Second", "Group B", "acc1")
    third = app.SearchProfile("3", "Third", "Group A", "acc1")
    window.profiles = [first, second, third]
    window.refresh_ui()

    group_a = window.tree.topLevelItem(0)
    group_b = window.tree.topLevelItem(1)
    moved_item = group_a.takeChild(0)
    group_b.insertChild(0, moved_item)

    window._sync_profile_order()

    assert [profile.name for profile in window.profiles] == ["Third", "First", "Second"]
    assert first.group == "Group B"
    assert second.group == "Group B"
    assert third.group == "Group A"

    window.close()
    qapp.processEvents()


def test_main_window_labels_navigation_and_destructive_actions_clearly(tmp_path, monkeypatch):
    qapp = QApplication.instance() or QApplication(sys.argv)
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "config_v1.json")
    monkeypatch.setattr(app, "DOCS_DB", tmp_path / "documents.json")

    window = app.MainWindow()

    tab_labels = [window.tabs.tabText(i) for i in range(window.tabs.count())]
    assert "⚙️ Einstellungen" in tab_labels
    assert "📝 Protokoll" in tab_labels
    assert window.btn_delete_profile.text() == "❌ Profil löschen"
    assert window.btn_delete_account.text() == "❌ Account löschen"
    assert window.btn_browse_path.text() == "Ordner wählen..."
    assert window.btn_delete_profile.toolTip() == "Ausgewähltes Suchprofil löschen"
    assert window.tabs.tabToolTip(tab_labels.index("⚙️ Einstellungen")) == "Globale Einstellungen und Scheduler konfigurieren"

    window.close()
    qapp.processEvents()


def test_worker_runs_all_active_profiles_grouped_by_account(tmp_path, monkeypatch):
    profiles = [
        app.SearchProfile("1", "First", "Group", "acc1"),
        app.SearchProfile("2", "Inactive", "Group", "acc1", active=False),
        app.SearchProfile("3", "Second", "Group", "acc1"),
        app.SearchProfile("4", "Third", "Group", "acc2"),
    ]
    accounts = [
        app.MailAccount("acc1", "imap.example.org", "one@example.org"),
        app.MailAccount("acc2", "imap.example.org", "two@example.org"),
    ]
    worker = app.GrabberWorker(
        profiles,
        accounts,
        app.DownloadSettings(enable_hash_check=False),
        tmp_path,
        [],
    )
    connect_calls = []
    process_calls = []

    class FakeConn:
        def __init__(self, name):
            self.name = name
            self.logged_out = False

        def logout(self):
            self.logged_out = True

    def fake_connect(account_name):
        connect_calls.append(account_name)
        return FakeConn(account_name)

    def fake_process(conn, profile, settings):
        process_calls.append((conn.name, profile.name, settings))

    monkeypatch.setattr(worker, "connect_imap", fake_connect)
    monkeypatch.setattr(worker, "process_profile", fake_process)

    worker.run()

    assert connect_calls == ["acc1", "acc2"]
    assert [(conn_name, profile_name) for conn_name, profile_name, _ in process_calls] == [
        ("acc1", "First"),
        ("acc1", "Second"),
        ("acc2", "Third"),
    ]
    assert all(settings == worker.global_settings for _, _, settings in process_calls)


def test_process_profile_uses_gmail_raw_when_supported(tmp_path, monkeypatch):
    profile = app.SearchProfile(
        "1",
        "Invoices",
        "Mail",
        "acc1",
        query_sender="billing@example.org",
        gmail_query="has:attachment label:finance",
    )
    worker = app.GrabberWorker(
        [profile],
        [app.MailAccount("acc1", "imap.gmail.com", "user@example.org")],
        app.DownloadSettings(),
        tmp_path,
        [],
        datetime(2026, 5, 1),
    )
    seen = {"search": None, "processed": []}

    class FakeConn:
        capabilities = ("IMAP4REV1", "X-GM-EXT-1")

        def search(self, *args):
            seen["search"] = args
            return "OK", [b"1 2"]

    monkeypatch.setattr(
        worker,
        "process_email",
        lambda conn, num, dl_dir, settings, profile_name: seen["processed"].append(
            (num, dl_dir, profile_name)
        ),
    )

    worker.process_profile(FakeConn(), profile, worker.global_settings)

    assert seen["search"][0:2] == (None, "X-GM-RAW")
    assert "has:attachment label:finance" in seen["search"][2]
    assert 'from:\\"billing@example.org\\"' in seen["search"][2]
    assert "after:2026/05/01" in seen["search"][2]
    assert [num for num, _, _ in seen["processed"]] == [b"1", b"2"]


def test_build_imap_search_args_uses_english_month_names(tmp_path):
    """SINCE-Datum muss englische Monats-Abkürzungen verwenden (RFC 3501), nicht locale-abhängige."""
    worker = app.GrabberWorker(
        [],
        [],
        app.DownloadSettings(),
        tmp_path,
        [],
        datetime(2026, 10, 15),  # Oktober: "Okt" DE vs "Oct" EN
    )
    profile = app.SearchProfile("1", "Test", "G", "acc1")
    args = worker.build_imap_search_args(profile)
    since_val = args[args.index("SINCE") + 1]
    assert since_val == "15-Oct-2026", f"Falsches Datumsformat: {since_val!r}"
    # Sicherstellen dass kein DE-Monatsname enthalten ist
    assert "Okt" not in since_val
    assert "Mär" not in since_val
    assert "Mai" not in since_val


def test_process_profile_falls_back_to_imap_filters_without_gmail_extension(tmp_path, monkeypatch):
    profile = app.SearchProfile(
        "1",
        "Invoices",
        "Mail",
        "acc1",
        query_subject="Invoice",
        query_sender="billing@example.org",
        gmail_query="has:attachment",
    )
    worker = app.GrabberWorker(
        [profile],
        [app.MailAccount("acc1", "imap.example.org", "user@example.org")],
        app.DownloadSettings(),
        tmp_path,
        [],
        datetime(2026, 5, 1),
    )
    seen = {"search": None, "processed": []}

    class FakeConn:
        capabilities = ("IMAP4REV1",)

        def search(self, *args):
            seen["search"] = args
            return "OK", [b"7"]

    monkeypatch.setattr(
        worker,
        "process_email",
        lambda conn, num, dl_dir, settings, profile_name: seen["processed"].append(
            (num, dl_dir, profile_name)
        ),
    )

    worker.process_profile(FakeConn(), profile, worker.global_settings)

    assert seen["search"] == (
        None,
        "FROM",
        '"billing@example.org"',
        "SUBJECT",
        '"Invoice"',
        "SINCE",
        "01-May-2026",
    )
    assert seen["processed"] == [(b"7", tmp_path / "Invoices", "Invoices")]
