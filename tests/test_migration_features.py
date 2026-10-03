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
        def uid(self, command, *args):
            if command.lower() == "fetch":
                return "OK", [(b"1 (RFC822 {1})", msg.as_bytes())]
            return "OK", [b""]

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
    assert not window.btn_delete_profile.isEnabled()
    assert not window.btn_delete_account.isEnabled()
    assert window.btn_delete_profile.toolTip() == "Wählen Sie zuerst ein Suchprofil aus."
    assert window.btn_delete_account.toolTip() == "Wählen Sie zuerst einen IMAP-Account aus."
    assert window.tabs.tabToolTip(tab_labels.index("⚙️ Einstellungen")) == "Globale Einstellungen und Scheduler konfigurieren"

    window.close()
    qapp.processEvents()


def test_main_window_primary_controls_expose_accessible_context(tmp_path, monkeypatch):
    qapp = QApplication.instance() or QApplication(sys.argv)
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "config_v1.json")
    monkeypatch.setattr(app, "DOCS_DB", tmp_path / "documents.json")

    window = app.MainWindow()

    assert window.cb_time.accessibleName() == "Zeitraum auswählen"
    assert window.cb_time.toolTip() == "Zeitraum für den nächsten Profil-Lauf wählen"
    assert window.btn_add_profile.accessibleName() == "Profil hinzufügen"
    assert window.btn_add_profile.toolTip() == "Neues Suchprofil anlegen"
    assert window.btn_add_account.accessibleName() == "Account hinzufügen"
    assert window.btn_add_account.toolTip() == "Neuen IMAP-Account anlegen"
    assert window.ip_path.accessibleName() == "Download-Pfad"
    assert window.ck_att.accessibleName() == "Anhänge herunterladen"
    assert window.ck_pdf.accessibleName() == "Mail-Body als PDF speichern"
    assert window.ck_hash.accessibleName() == "Hash-Deduplizierung"
    assert window.ip_fmt.accessibleName() == "Erlaubte Formate"
    assert window.btn_save_settings.accessibleName() == "Globale Einstellungen speichern"
    assert window.cb_scheduler.accessibleName() == "Scheduler-Intervall"
    assert window.btn_save_scheduler.accessibleName() == "Scheduler speichern"
    assert window.btn_delete_profile.accessibleDescription() == "Deaktiviert, bis ein Suchprofil ausgewählt ist."
    assert window.btn_delete_account.accessibleDescription() == "Deaktiviert, bis ein IMAP-Account ausgewählt ist."

    window.close()
    qapp.processEvents()


def test_delete_buttons_enable_only_for_real_selection(tmp_path, monkeypatch):
    qapp = QApplication.instance() or QApplication(sys.argv)
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "config_v1.json")
    monkeypatch.setattr(app, "DOCS_DB", tmp_path / "documents.json")

    window = app.MainWindow()
    window.accounts = [app.MailAccount("Konto A", "imap.example.org", "mail@example.org")]
    window.profiles = [app.SearchProfile("1", "Rechnungen", "Standard", "Konto A")]
    window.refresh_ui()
    qapp.processEvents()

    assert not window.btn_delete_profile.isEnabled()
    assert not window.btn_delete_account.isEnabled()

    profile_group = window.tree.topLevelItem(0)
    profile_item = profile_group.child(0)
    window.tree.setCurrentItem(profile_group)
    qapp.processEvents()
    assert not window.btn_delete_profile.isEnabled()

    window.tree.setCurrentItem(profile_item)
    qapp.processEvents()
    assert window.btn_delete_profile.isEnabled()
    assert window.btn_delete_profile.toolTip() == "Ausgewähltes Suchprofil löschen"
    assert window.btn_delete_profile.accessibleDescription() == "Löscht das aktuell ausgewählte Suchprofil."

    window.list_acc.selectRow(0)
    qapp.processEvents()
    assert window.btn_delete_account.isEnabled()
    assert window.btn_delete_account.toolTip() == "Ausgewählten IMAP-Account löschen"
    assert window.btn_delete_account.accessibleDescription() == "Löscht den aktuell ausgewählten IMAP-Account."

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
    seen = {"uid_search": None, "processed": []}

    class FakeConn:
        capabilities = ("IMAP4REV1", "X-GM-EXT-1")

        def uid(self, command, *args):
            if command.lower() == "search":
                seen["uid_search"] = args
                return "OK", [b"1 2"]
            return "OK", [b""]

    monkeypatch.setattr(
        worker,
        "process_email",
        lambda conn, num, dl_dir, settings, profile_name: seen["processed"].append(
            (num, dl_dir, profile_name)
        ),
    )

    worker.process_profile(FakeConn(), profile, worker.global_settings)

    # uid('search', *search_args[1:]) — kein Charset-Argument; erster Arg ist X-GM-RAW
    assert seen["uid_search"][0] == "X-GM-RAW"
    assert "has:attachment label:finance" in seen["uid_search"][1]
    assert 'from:\\"billing@example.org\\"' in seen["uid_search"][1]
    assert "after:2026/05/01" in seen["uid_search"][1]
    assert [num for num, _, _ in seen["processed"]] == [b"1", b"2"]


def test_close_event_stops_running_worker(tmp_path, monkeypatch):
    """closeEvent muss requestInterruption + wait() auf laufenden Worker aufrufen."""
    qapp = QApplication.instance() or QApplication(sys.argv)
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "config_v1.json")
    monkeypatch.setattr(app, "DOCS_DB", tmp_path / "documents.json")

    window = app.MainWindow()
    calls = []

    class FakeWorker:
        def isRunning(self):
            return True

        def requestInterruption(self):
            calls.append("interrupt")

        def wait(self, ms):
            calls.append(f"wait({ms})")

    window.worker = FakeWorker()

    from PySide6.QtGui import QCloseEvent
    window.closeEvent(QCloseEvent())

    assert "interrupt" in calls
    assert any("wait" in c for c in calls)

    window.close()
    qapp.processEvents()


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


def test_save_attachment_skips_none_payload(tmp_path):
    """_save_attachment muss False zurückgeben und keine Datei anlegen wenn get_payload None liefert."""
    worker = app.GrabberWorker([], [], app.DownloadSettings(), tmp_path, [])

    class FakePart:
        def get_filename(self):
            return "attachment.pdf"

        def get_payload(self, decode=False):
            return None

    settings = app.DownloadSettings(download_attachments=True, formats=["pdf"])
    result = worker._save_attachment(FakePart(), "mail_001", tmp_path, settings, "Prof", "2026-06-21", "s@s.de", "Sub")

    assert result is False
    assert not (tmp_path / "mail_001_ATT.pdf").exists()


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
    seen = {"uid_search": None, "processed": []}

    class FakeConn:
        capabilities = ("IMAP4REV1",)

        def uid(self, command, *args):
            if command.lower() == "search":
                seen["uid_search"] = args
                return "OK", [b"7"]
            return "OK", [b""]

    monkeypatch.setattr(
        worker,
        "process_email",
        lambda conn, num, dl_dir, settings, profile_name: seen["processed"].append(
            (num, dl_dir, profile_name)
        ),
    )

    worker.process_profile(FakeConn(), profile, worker.global_settings)

    # uid('search', *search_args[1:]) — kein Charset-Argument, direkt IMAP-Kriterien
    assert seen["uid_search"] == (
        "FROM",
        '"billing@example.org"',
        "SUBJECT",
        '"Invoice"',
        "SINCE",
        "01-May-2026",
    )
    assert seen["processed"] == [(b"7", tmp_path / "Invoices", "Invoices")]



def _write_identity_fixture(tmp_path, names):
    import json

    config_path = tmp_path / "config_v1.json"
    docs_path = tmp_path / "documents.json"
    accounts = [
        {
            "name": name,
            "host": "imap.synthetic.invalid",
            "user": f"user-{index}@example.invalid",
            "port": 993,
            "search_folder": "INBOX",
        }
        for index, name in enumerate(names, start=1)
    ]
    config = {
        "base_path": str(tmp_path / "downloads"),
        "global_settings": {},
        "profiles": [
            {
                "id": "profile-one",
                "name": "Profile One",
                "group": "Synthetic",
                "account_name": names[0],
                "active": True,
            },
            {
                "id": "profile-two",
                "name": "Profile Two",
                "group": "Synthetic",
                "account_name": names[-1],
                "active": False,
            },
        ],
        "accounts": accounts,
        "scheduler_interval": 5,
        "fixture_marker": "preserve-original-bytes-while-blocked",
    }
    documents = [
        app.Document(
            "Profile One", "synthetic.pdf", "2026-10-02", str(tmp_path / "synthetic.pdf"),
            "sender@example.invalid", "Synthetic subject",
        ).to_dict()
    ]
    config_bytes = (json.dumps(config, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    docs_bytes = (json.dumps(documents, separators=(",", ":")) + "\n").encode("utf-8")
    config_path.write_bytes(config_bytes)
    docs_path.write_bytes(docs_bytes)
    return config_path, docs_path, config_bytes, docs_bytes


def test_invalid_loaded_identities_preserve_candidates_and_block_all_autosaves(tmp_path, monkeypatch):
    qapp = QApplication.instance() or QApplication(sys.argv)
    config_path, docs_path, config_bytes, docs_bytes = _write_identity_fixture(
        tmp_path, ["Billing", " billing ", "BILLING"]
    )
    monkeypatch.setattr(app, "CONFIG_FILE", config_path)
    monkeypatch.setattr(app, "DOCS_DB", docs_path)

    window = app.MainWindow()
    assert [account.name for account in window.accounts] == ["Billing", " billing ", "BILLING"]
    assert [profile.id for profile in window.profiles] == ["profile-one", "profile-two"]
    assert len(window.documents) == 1
    assert not window.account_identity_notice.isHidden()
    assert not window._scheduler_timer.isActive()
    assert not window.btn_start.isEnabled()

    # A still-pending load error remains a blocker even if an in-memory list is changed.
    window.accounts = [window.accounts[0]]
    assert window._account_identity_error
    assert window.save_config() is False
    keyring_calls = []
    dialog_constructions = []

    class AddDialog:
        def __init__(self, *args, **kwargs):
            dialog_constructions.append(True)
        def exec(self):
            return True
        def get_data(self):
            return app.MailAccount("Archive", "imap.synthetic.invalid", "new@example.invalid"), "fake-secret"

    monkeypatch.setattr(app, "AccountDialog", AddDialog)
    monkeypatch.setattr(app, "KEYRING_AVAIL", True)
    monkeypatch.setattr(app.keyring, "set_password", lambda *args: keyring_calls.append(args))
    window.add_acc()
    assert dialog_constructions == []
    assert keyring_calls == []

    window.run_all()
    assert window.worker is None
    window.save_glob()
    window._save_scheduler()
    window._on_scheduler_tick()
    window.on_finished()
    window.tree.setCurrentItem(window.tree.topLevelItem(0).child(0))
    window.del_prof()
    window._sync_profile_order()

    assert [profile.id for profile in window.profiles] == ["profile-one", "profile-two"]
    assert config_path.read_bytes() == config_bytes
    assert docs_path.read_bytes() == docs_bytes
    window.close()
    qapp.processEvents()


def test_explicit_account_deletes_recheck_all_candidates_before_unblocking(tmp_path, monkeypatch):
    import json

    qapp = QApplication.instance() or QApplication(sys.argv)
    config_path, docs_path, config_bytes, docs_bytes = _write_identity_fixture(
        tmp_path, ["Billing", " billing ", "BILLING"]
    )
    monkeypatch.setattr(app, "CONFIG_FILE", config_path)
    monkeypatch.setattr(app, "DOCS_DB", docs_path)

    window = app.MainWindow()
    window.list_acc.selectRow(0)
    window.del_acc()
    assert [account.name for account in window.accounts] == [" billing ", "BILLING"]
    assert window._account_identity_error
    assert config_path.read_bytes() == config_bytes
    assert docs_path.read_bytes() == docs_bytes

    window.list_acc.selectRow(0)
    window.del_acc()
    assert [account.name for account in window.accounts] == ["BILLING"]
    assert window._account_identity_error is None
    assert window.account_identity_notice.isHidden()
    assert window.btn_start.isEnabled()
    saved_config = json.loads(config_path.read_text(encoding="utf-8"))
    saved_docs = json.loads(docs_path.read_text(encoding="utf-8"))
    assert [account["name"] for account in saved_config["accounts"]] == ["BILLING"]
    assert [profile["id"] for profile in saved_config["profiles"]] == ["profile-one", "profile-two"]
    assert saved_docs[0]["filename"] == "synthetic.pdf"
    window.close()
    qapp.processEvents()


def test_new_account_collision_is_rejected_before_keyring_or_config_write(tmp_path, monkeypatch):
    qapp = QApplication.instance() or QApplication(sys.argv)
    config_path, docs_path, config_bytes, docs_bytes = _write_identity_fixture(
        tmp_path, ["Billing"]
    )
    monkeypatch.setattr(app, "CONFIG_FILE", config_path)
    monkeypatch.setattr(app, "DOCS_DB", docs_path)
    window = app.MainWindow()
    keyring_calls = []
    warnings = []

    class AddDialog:
        def __init__(self, *args, **kwargs):
            pass
        def exec(self):
            return True
        def get_data(self):
            return app.MailAccount(" billing ", "imap.synthetic.invalid", "dup@example.invalid"), "fake-secret"

    monkeypatch.setattr(app, "AccountDialog", AddDialog)
    monkeypatch.setattr(app, "KEYRING_AVAIL", True)
    monkeypatch.setattr(app.keyring, "set_password", lambda *args: keyring_calls.append(args))
    monkeypatch.setattr(app.QMessageBox, "warning", lambda *args: warnings.append(args))

    window.add_acc()

    assert [account.name for account in window.accounts] == ["Billing"]
    assert keyring_calls == []
    assert len(warnings) == 1
    assert config_path.read_bytes() == config_bytes
    assert docs_path.read_bytes() == docs_bytes
    window.close()
    qapp.processEvents()



def test_valid_new_account_is_saved_under_original_name_after_keyring_write(tmp_path, monkeypatch):
    import json

    qapp = QApplication.instance() or QApplication(sys.argv)
    config_path, docs_path, _config_bytes, _docs_bytes = _write_identity_fixture(
        tmp_path, ["Billing"]
    )
    monkeypatch.setattr(app, "CONFIG_FILE", config_path)
    monkeypatch.setattr(app, "DOCS_DB", docs_path)
    window = app.MainWindow()
    keyring_calls = []

    class AddDialog:
        def __init__(self, *args, **kwargs):
            pass
        def exec(self):
            return True
        def get_data(self):
            return app.MailAccount("Archive", "imap.synthetic.invalid", "archive@example.invalid"), "fake-secret"

    monkeypatch.setattr(app, "AccountDialog", AddDialog)
    monkeypatch.setattr(app, "KEYRING_AVAIL", True)
    monkeypatch.setattr(app.keyring, "set_password", lambda *args: keyring_calls.append(args))

    window.add_acc()

    assert keyring_calls == [(app.APP_NAME, "Archive", "fake-secret")]
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert [account["name"] for account in saved["accounts"]] == ["Billing", "Archive"]
    assert window._account_identity_error is None
    window.close()
    qapp.processEvents()


def test_repair_save_io_error_keeps_blocker_and_original_bytes(tmp_path, monkeypatch):
    qapp = QApplication.instance() or QApplication(sys.argv)
    config_path, docs_path, config_bytes, docs_bytes = _write_identity_fixture(
        tmp_path, ["Billing", " billing "]
    )
    monkeypatch.setattr(app, "CONFIG_FILE", config_path)
    monkeypatch.setattr(app, "DOCS_DB", docs_path)
    warnings = []
    monkeypatch.setattr(app.QMessageBox, "warning", lambda *args: warnings.append(args))
    window = app.MainWindow()
    original_error = window._account_identity_error
    window.accounts = [window.accounts[0]]

    original_write_text = Path.write_text
    def fail_config_write(target, *args, **kwargs):
        if target == config_path:
            raise OSError("synthetic write failure")
        return original_write_text(target, *args, **kwargs)

    monkeypatch.setattr(Path, "write_text", fail_config_write)
    assert window.save_config(allow_identity_repair=True) is False
    assert window._account_identity_error == original_error
    assert len(warnings) == 1
    assert config_path.read_bytes() == config_bytes
    assert docs_path.read_bytes() == docs_bytes
    window.close()
    qapp.processEvents()


def test_run_all_shows_worker_identity_error_in_gui(tmp_path, monkeypatch):
    qapp = QApplication.instance() or QApplication(sys.argv)
    config_path, docs_path, _config_bytes, _docs_bytes = _write_identity_fixture(
        tmp_path, ["Billing"]
    )
    monkeypatch.setattr(app, "CONFIG_FILE", config_path)
    monkeypatch.setattr(app, "DOCS_DB", docs_path)
    warnings = []
    monkeypatch.setattr(app.QMessageBox, "warning", lambda *args: warnings.append(args))

    class InvalidWorker:
        def __init__(self, *args, **kwargs):
            raise app.AccountIdentityError("synthetic concurrent name collision")

    monkeypatch.setattr(app, "GrabberWorker", InvalidWorker)
    window = app.MainWindow()
    window.run_all()

    assert window.worker is None
    assert window._account_identity_error == "synthetic concurrent name collision"
    assert "synthetic concurrent name collision" in window.log.toPlainText()
    assert len(warnings) == 1
    assert not window.btn_start.isEnabled()
    window.close()
    qapp.processEvents()


def test_invalid_account_notice_retranslates_and_keeps_disk_blocked(tmp_path, monkeypatch):
    import json

    qapp = QApplication.instance() or QApplication(sys.argv)
    config_path, docs_path, _config_bytes, docs_bytes = _write_identity_fixture(
        tmp_path, ["Billing", " billing "]
    )
    config = json.loads(config_path.read_text(encoding="utf-8"))
    config["language"] = "en"
    config_path.write_text(
        json.dumps(config, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    config_bytes = config_path.read_bytes()
    monkeypatch.setattr(app, "CONFIG_FILE", config_path)
    monkeypatch.setattr(app, "DOCS_DB", docs_path)

    window = app.MainWindow()
    assert window.language == "en"
    assert not window.btn_start.isEnabled()
    assert not window.account_identity_notice.isHidden()

    rendered = set()
    for language in ("de", "en", "es", "zh", "ja", "ru"):
        window.set_ui_language(language)
        translator = window.translator
        detail = window._account_identity_details.translated(translator)
        expected = translator.t(
            "UI_ACCOUNT_IDENTITY_BLOCKED",
            error=detail,
        )
        assert window.account_identity_notice.text() == expected
        assert window.lbl_scheduler_status.text() == translator.t(
            "UI_SCHEDULER_IDENTITY_BLOCKED"
        )
        assert translator.t("ACC_ACCOUNT_IDENTITY_NOTICE") == (
            window.account_identity_notice.accessibleName()
        )
        assert window.save_config() is False
        assert not window.btn_start.isEnabled()
        assert config_path.read_bytes() == config_bytes
        assert docs_path.read_bytes() == docs_bytes
        rendered.add(window.account_identity_notice.text())

    assert len(rendered) == 6
    window.close()
    qapp.processEvents()
