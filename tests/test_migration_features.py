"""Regression tests for migrated UniversalDocsGrabber features."""

import os
import sys
from email.message import EmailMessage
from pathlib import Path
from types import SimpleNamespace

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
