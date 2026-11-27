# -*- coding: utf-8 -*-
"""
Runtime, Scheduler, Converter, CLI & Web-Companion Cross-Boundary Contract Tests
================================================================================

Covers:
1. MainWindow.run_all() localized time filter & running button text across all 6 UI languages.
2. MainWindow scheduler lifecycle (_save_scheduler, _apply_scheduler, _on_scheduler_tick).
3. GrabberWorker.run() & process_profile() orchestration (multi-account, inactive skip,
   failed connection handling, interruption guard, X-GM-RAW vs IMAP fallback, 30-UID cap,
   enable_hash_check deduplication trigger).
4. UniversalConverter.convert_to_pdf() (.pdf identity, non-empty reuse, 0-byte cleanup,
   real .txt -> .pdf & .png -> .pdf conversion).
5. app_icon_loader.py root resolution (_MEIPASS vs source) & offscreen QIcon loading.
6. CLI edge cases (--list-documents --category/--limit 0, has_cli_action '=' syntax,
   --export-csv protected path JSON error) and cross-boundary Python -> Node.js
   Web Companion library.js compatibility for both GUI and CLI exports.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

import app_icon_loader
import cli
import UniversalDocsGrabberV1 as app
from translator import TranslationSystem, get_translator

ROOT = Path(__file__).resolve().parent.parent


@pytest.fixture(scope="module")
def qapp():
    inst = QApplication.instance()
    if inst is None:
        inst = QApplication([])
    return inst


@pytest.fixture
def isolated_window(tmp_path, monkeypatch, qapp):
    cfg_file = tmp_path / "config_v1.json"
    docs_file = tmp_path / "documents.json"
    monkeypatch.setattr(app, "CONFIG_FILE", cfg_file)
    monkeypatch.setattr(app, "DOCS_DB", docs_file)
    # Restore singleton translator language after test
    orig_lang = get_translator().current_lang
    win = app.MainWindow()
    win.base_path = str(tmp_path / "downloads")
    yield win, cfg_file, docs_file
    win._scheduler_timer.stop()
    win.close()
    get_translator().set_language(orig_lang)


def test_run_all_time_filter_works_across_all_six_languages(isolated_window, monkeypatch):
    """MainWindow.run_all() must honor cb_time selection regardless of active UI language."""
    win, _, _ = isolated_window
    captured_dates = []

    class DummyWorker:
        def __init__(self, profiles, accounts, global_settings, base_path, db, date_override=None):
            captured_dates.append(date_override)
            self.active_profile_count = 0
            self.log = _DummySignal()
            self.progress = _DummySignal()
            self.finished = _DummySignal()

        def isRunning(self):
            return False

        def start(self):
            pass

    monkeypatch.setattr(app, "GrabberWorker", DummyWorker)
    today = date.today()

    for lang in TranslationSystem.SUPPORTED_LANGUAGES:
        win.set_ui_language(lang)

        # Index 0: All -> None
        win.cb_time.setCurrentIndex(0)
        win.run_all()
        assert captured_dates[-1] is None, f"lang={lang} idx=0 expected None"

        # Index 1: This year -> Jan 1 of current year
        win.cb_time.setCurrentIndex(1)
        win.run_all()
        assert captured_dates[-1] == datetime(today.year, 1, 1), f"lang={lang} idx=1 failed"

        # Index 2: Last year -> Jan 1 of previous year
        win.cb_time.setCurrentIndex(2)
        win.run_all()
        assert captured_dates[-1] == datetime(today.year - 1, 1, 1), f"lang={lang} idx=2 failed"

        # Index 3: Last month -> ~30 days ago
        win.cb_time.setCurrentIndex(3)
        win.run_all()
        delta = datetime.now() - captured_dates[-1]
        assert timedelta(days=29) <= delta <= timedelta(days=31), f"lang={lang} idx=3 failed"


def test_run_all_button_running_text_is_localized(isolated_window, monkeypatch):
    """btn_start text during run_all() must use the active UI language translation."""
    win, _, _ = isolated_window

    class DummyWorker:
        def __init__(self, *args, **kwargs):
            self.active_profile_count = 0
            self.log = _DummySignal()
            self.progress = _DummySignal()
            self.finished = _DummySignal()

        def isRunning(self):
            return False

        def start(self):
            pass

    monkeypatch.setattr(app, "GrabberWorker", DummyWorker)
    win.set_ui_language("en")
    win.run_all()
    assert win.btn_start.text() == get_translator("en").t("UI_BTN_RUNNING")


class _DummySignal:
    def connect(self, _cb):
        pass

    def emit(self, *args):
        pass


def test_save_scheduler_and_apply_scheduler_persists_interval(isolated_window):
    """_save_scheduler persists interval to config_v1.json and starts/stops QTimer."""
    win, cfg_file, _ = isolated_window
    idx_30 = app.SCHEDULER_INTERVALS.index(30)
    win.cb_scheduler.setCurrentIndex(idx_30)
    win._save_scheduler()

    assert win.scheduler_interval == 30
    assert win._scheduler_timer.isActive() is True
    saved = json.loads(cfg_file.read_text(encoding="utf-8"))
    assert saved["scheduler_interval"] == 30

    idx_off = app.SCHEDULER_INTERVALS.index(0)
    win.cb_scheduler.setCurrentIndex(idx_off)
    win._save_scheduler()
    assert win.scheduler_interval == 0
    assert win._scheduler_timer.isActive() is False


def test_on_scheduler_tick_skips_running_worker_and_stops_on_identity_error(isolated_window, monkeypatch):
    """_on_scheduler_tick must skip when worker is running and stop timer when identity error exists."""
    win, _, _ = isolated_window
    win.scheduler_interval = 15
    win._apply_scheduler()
    assert win._scheduler_timer.isActive() is True

    calls = []
    monkeypatch.setattr(win, "run_all", lambda: calls.append("run_all"))

    class RunningWorker:
        def isRunning(self):
            return True

    win.worker = RunningWorker()
    win._on_scheduler_tick()
    assert calls == []
    assert "übersprungen" in win.log.toPlainText()

    # Duplicate account triggers identity block -> timer must stop
    win.worker = None
    win.accounts = [
        app.MailAccount("Work", "imap.example.org", "a@example.org"),
        app.MailAccount(" work ", "imap.example.org", "b@example.org"),
    ]
    win._on_scheduler_tick()
    assert calls == []
    assert win._scheduler_timer.isActive() is False


def test_worker_run_groups_accounts_skips_inactive_and_triggers_dedup(tmp_path, monkeypatch):
    """GrabberWorker.run() handles active/inactive filtering, failed connects, logout, and deduplication."""
    accounts = [
        app.MailAccount("FailAcc", "imap.fail.example", "f@example.org"),
        app.MailAccount("OkAcc", "imap.ok.example", "o@example.org"),
    ]
    profiles = [
        app.SearchProfile("p1", "ActiveFail", "G", "FailAcc", active=True),
        app.SearchProfile("p2", "InactiveOk", "G", "OkAcc", active=False),
        app.SearchProfile("p3", "ActiveOk", "G", "OkAcc", active=True),
    ]
    settings = app.DownloadSettings(enable_hash_check=True)
    worker = app.GrabberWorker(profiles, accounts, settings, tmp_path, [])

    progress_events = []
    processed_profiles = []
    dedup_calls = []
    logout_calls = []

    class FakeConn:
        def logout(self):
            logout_calls.append(True)

    worker.progress.connect(lambda cur, tot: progress_events.append((cur, tot)))
    monkeypatch.setattr(worker, "connect_imap", lambda name: FakeConn() if name == "OkAcc" else None)
    monkeypatch.setattr(worker, "process_profile", lambda conn, prof, eff: processed_profiles.append(prof.name))
    monkeypatch.setattr(worker, "run_deduplication", lambda: dedup_calls.append(True))

    worker.run()

    assert worker.active_profile_count == 2
    assert processed_profiles == ["ActiveOk"]
    assert progress_events == [(0, 2), (1, 2), (2, 2)]
    assert logout_calls == [True]
    assert dedup_calls == [True]


def test_worker_run_respects_interruption_request(tmp_path, monkeypatch):
    """GrabberWorker.run() exits before connecting if interruption was requested."""
    accounts = [app.MailAccount("OkAcc", "imap.ok.example", "o@example.org")]
    profiles = [app.SearchProfile("p1", "ActiveOk", "G", "OkAcc", active=True)]
    worker = app.GrabberWorker(profiles, accounts, app.DownloadSettings(enable_hash_check=False), tmp_path, [])

    connect_calls = []
    monkeypatch.setattr(worker, "isInterruptionRequested", lambda: True)
    monkeypatch.setattr(worker, "connect_imap", lambda name: connect_calls.append(name))

    worker.run()
    assert connect_calls == []


def test_process_profile_gmail_raw_fallback_and_30_uid_cap(tmp_path, monkeypatch):
    """process_profile uses X-GM-RAW when supported, falls back otherwise, and caps to last 30 UIDs."""
    prof = app.SearchProfile(
        "p1",
        "GmailProf",
        "G",
        "Acc",
        gmail_query="has:attachment",
        query_subject="Invoice",
    )
    worker = app.GrabberWorker([prof], [], app.DownloadSettings(), tmp_path, [])

    search_calls = []
    fetched_uids = []

    class FakeImap:
        def __init__(self, capabilities, uids):
            self.capabilities = capabilities
            self._uids = uids

        def uid(self, cmd, *args):
            if cmd == "search":
                search_calls.append(args)
                return "OK", [b" ".join(self._uids)]
            return "OK", []

    monkeypatch.setattr(worker, "process_email", lambda conn, uid, dl_dir, settings, name: fetched_uids.append(uid))

    # 1. Server with X-GM-EXT-1 and 35 UIDs -> X-GM-RAW + last 30 UIDs
    uids_35 = [str(i).encode("ascii") for i in range(1, 36)]
    conn_gm = FakeImap((b"IMAP4rev1", b"X-GM-EXT-1"), uids_35)
    worker.process_profile(conn_gm, prof, worker.global_settings)
    assert search_calls[0][0] == "X-GM-RAW"
    assert len(fetched_uids) == 30
    assert fetched_uids[0] == b"6" and fetched_uids[-1] == b"35"

    # 2. Server without X-GM-EXT-1 -> fallback to standard IMAP search args
    search_calls.clear()
    fetched_uids.clear()
    logs = []
    worker.log.connect(logs.append)
    conn_std = FakeImap((b"IMAP4rev1",), [b"10", b"11"])
    worker.process_profile(conn_std, prof, worker.global_settings)
    assert search_calls[0][0] == "SUBJECT"
    assert fetched_uids == [b"10", b"11"]
    assert any("Fallback" in msg for msg in logs)


def test_converter_convert_to_pdf_shortcuts_zero_byte_and_real_outputs(tmp_path):
    """UniversalConverter.convert_to_pdf handles .pdf identity, 0-byte cleanup, .txt and .png."""
    from PIL import Image

    logs = []
    conv = app.UniversalConverter(logs.append)

    # 1. .pdf file returns itself
    pdf_file = tmp_path / "direct.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 existing")
    assert conv.convert_to_pdf(pdf_file) == pdf_file

    # 2. .txt with 0-byte stale .pdf sibling removes stale .pdf and creates real PDF
    txt_file = tmp_path / "notes.txt"
    txt_file.write_text("Line 1: Invoice 2026\nLine 2: Total 42.00 EUR\n", encoding="utf-8")
    stale_pdf = tmp_path / "notes.pdf"
    stale_pdf.write_bytes(b"")
    out_txt_pdf = conv.convert_to_pdf(txt_file)
    assert out_txt_pdf == stale_pdf
    assert out_txt_pdf.stat().st_size > 100
    assert out_txt_pdf.read_bytes().startswith(b"%PDF-")

    # 3. Non-empty existing target .pdf is reused directly
    mtime_before = out_txt_pdf.stat().st_mtime_ns
    assert conv.convert_to_pdf(txt_file) == out_txt_pdf
    assert out_txt_pdf.stat().st_mtime_ns == mtime_before

    # 4. .png image converts to valid PDF
    png_file = tmp_path / "scan.png"
    Image.new("RGB", (32, 32), color=(20, 80, 140)).save(png_file)
    out_img_pdf = conv.convert_to_pdf(png_file)
    assert out_img_pdf is not None
    assert out_img_pdf.exists()
    assert out_img_pdf.read_bytes().startswith(b"%PDF-")


def test_app_icon_loader_root_and_offscreen_icon(tmp_path, monkeypatch, qapp):
    """app_icon_loader resolves _MEIPASS vs source root and returns a valid non-null QIcon."""
    assert app_icon_loader.get_project_root() == ROOT
    monkeypatch.setattr(sys, "_MEIPASS", str(tmp_path), raising=False)
    assert app_icon_loader.get_project_root() == tmp_path

    monkeypatch.delattr(sys, "_MEIPASS", raising=False)
    icon = app_icon_loader.get_app_icon()
    assert isinstance(icon, QIcon)
    assert not icon.isNull()


def test_cli_list_documents_category_filter_limit_zero_and_equals_flags(tmp_path, capsys):
    """cli.py supports --category filtering, --limit 0, '=' action detection, and JSON error on protected CSV."""
    assert cli.has_cli_action(["--export-library=out.json"]) is True
    assert cli.has_cli_action(["--export-csv=out.csv"]) is True

    downloads = tmp_path / "Downloads"
    cat_dir = downloads / "Steuern" / "Belege"
    cat_dir.mkdir(parents=True)
    doc1 = cat_dir / "bescheid.pdf"
    doc1.write_bytes(b"%PDF-1.4")

    other_dir = downloads / "Steuern" / "Sonstiges"
    other_dir.mkdir(parents=True)
    doc2 = other_dir / "notiz.pdf"
    doc2.write_bytes(b"%PDF-1.4")

    cfg = tmp_path / "config_v1.json"
    cfg.write_text(
        json.dumps({
            "base_path": str(downloads),
            "profiles": [{"name": "Steuern", "target_folder": "Steuern", "active": True}],
            "accounts": [],
        }),
        encoding="utf-8",
    )
    db = tmp_path / "documents.json"
    db.write_text(
        json.dumps([
            {"profile": "Steuern", "filename": "bescheid.pdf", "date": "2026-03-01", "path": str(doc1)},
            {"profile": "Steuern", "filename": "notiz.pdf", "date": "2026-03-02", "path": str(doc2)},
        ]),
        encoding="utf-8",
    )

    # Category filter
    rc = cli.run_cli([
        "--list-documents",
        "--category", "belege",
        "--json",
        "--config", str(cfg),
        "--documents-db", str(db),
    ])
    assert rc == 0
    res_cat = json.loads(capsys.readouterr().out)
    assert res_cat["total_count"] == 1
    assert res_cat["documents"][0]["filename"] == "bescheid.pdf"

    # --limit 0 returns all
    rc_all = cli.run_cli([
        "--list-documents",
        "--limit", "0",
        "--json",
        "--config", str(cfg),
        "--documents-db", str(db),
    ])
    assert rc_all == 0
    res_all = json.loads(capsys.readouterr().out)
    assert res_all["total_count"] == 2
    assert res_all["returned_count"] == 2

    # Protected CSV path returns exit 1 with structured JSON error
    from unittest.mock import patch
    with patch("cli.get_default_protected_paths", return_value={cfg.resolve()}):
        rc_err = cli.run_cli([
            "--export-csv", str(cfg),
            "--json",
            "--config", str(cfg),
            "--documents-db", str(db),
        ])
    assert rc_err == 1
    err_payload = json.loads(capsys.readouterr().out)
    assert err_payload["status"] == "error"


def test_cli_and_gui_exports_both_load_in_web_companion_library_js(tmp_path):
    """Cross-boundary contract: both GUI and CLI library exports must parse cleanly in web_companion/library.js."""
    node_exe = shutil.which("node")
    if not node_exe:
        pytest.skip("node executable not available")

    downloads = tmp_path / "UnivDocs"
    doc_dir = downloads / "Invoices" / "Rechnungen"
    doc_dir.mkdir(parents=True)
    pdf_file = doc_dir / "rechnung_01.pdf"
    pdf_file.write_bytes(b"%PDF-1.4 invoice")

    # 1. GUI export payload
    gui_payload = app.build_library_export_payload(
        profiles=[
            app.SearchProfile(
                "p1",
                "Invoices",
                "Finance",
                "Main",
                target_folder="Invoices",
                override_settings=app.DownloadSettings(
                    auto_categorize=True,
                    category_rules=[{"keyword": "rechnung", "folder": "Rechnungen"}],
                ),
            )
        ],
        accounts=[app.MailAccount("Main", "imap.example.org", "user@example.org")],
        documents=[app.Document("Invoices", "rechnung_01.pdf", "2026-11-23", str(pdf_file))],
        global_settings=app.DownloadSettings(category_rules=[{"keyword": "steuer", "folder": "Steuer"}]),
        base_path=downloads,
    )

    # 2. CLI export payload
    cli_payload = cli.build_library_export_payload(
        base_path_str=str(downloads),
        global_settings={"category_rules": [{"keyword": "steuer", "folder": "Steuer"}]},
        profiles=[
            {
                "id": "p1",
                "name": "Invoices",
                "group": "Finance",
                "account_name": "Main",
                "target_folder": "Invoices",
                "active": True,
                "override_settings": {
                    "auto_categorize": True,
                    "category_rules": [{"keyword": "rechnung", "folder": "Rechnungen"}],
                },
            }
        ],
        accounts=[{"name": "Main"}],
        scheduler_interval=15,
        documents=[{"profile": "Invoices", "filename": "rechnung_01.pdf", "date": "2026-11-23", "path": str(pdf_file)}],
    )

    gui_json = tmp_path / "gui_export.json"
    cli_json = tmp_path / "cli_export.json"
    gui_json.write_text(json.dumps(gui_payload, ensure_ascii=False), encoding="utf-8")
    cli_json.write_text(json.dumps(cli_payload, ensure_ascii=False), encoding="utf-8")

    lib_uri = (ROOT / "web_companion" / "library.js").as_uri()
    js_script = (
        "import fs from 'node:fs';\n"
        f"import {{ parseLibraryText }} from '{lib_uri}';\n"
        "for (const fp of process.argv.slice(1)) {\n"
        "  const parsed = parseLibraryText(fs.readFileSync(fp, 'utf8'));\n"
        "  const rechnungen = parsed.categories.find((c) => c.name === 'Rechnungen');\n"
        "  if (!rechnungen) throw new Error('Rechnungen category missing in ' + fp);\n"
        "  if (rechnungen.document_count !== 1) throw new Error('Expected document_count=1, got ' + rechnungen.document_count + ' in ' + fp);\n"
        "  if (!rechnungen.source || rechnungen.source === 'unknown') throw new Error('Expected source metadata in ' + fp);\n"
        "}\n"
    )
    proc = subprocess.run(
        [node_exe, "--input-type=module", "-e", js_script, str(gui_json), str(cli_json)],
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    assert proc.returncode == 0, f"Web Companion failed to parse export:\nSTDERR: {proc.stderr}\nSTDOUT: {proc.stdout}"
