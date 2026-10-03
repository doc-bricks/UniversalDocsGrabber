"""Regression tests for archive-derived progress and target-folder actions."""

import atexit
import os
import shutil
import sys
import tempfile
import threading
import time
from pathlib import Path
from types import SimpleNamespace

import pytest

_TEST_HOME = Path(tempfile.gettempdir()) / f"udg-archive-feature-{os.getpid()}"
_TEST_ENV = {
    "USERPROFILE": str(_TEST_HOME),
    "HOME": str(_TEST_HOME),
    "APPDATA": str(_TEST_HOME / "AppData" / "Roaming"),
    "LOCALAPPDATA": str(_TEST_HOME / "AppData" / "Local"),
    "QT_QPA_PLATFORM": "offscreen",
    "PYTHONDONTWRITEBYTECODE": "1",
}
_PREVIOUS_TEST_ENV = {key: os.environ.get(key) for key in _TEST_ENV}
_PREVIOUS_SYS_PATH = sys.path.copy()
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.update(_TEST_ENV)
try:
    import UniversalDocsGrabberV1 as app  # noqa: E402
    from PySide6.QtTest import QSignalSpy  # noqa: E402
    from PySide6.QtWidgets import QApplication  # noqa: E402
finally:
    sys.path[:] = _PREVIOUS_SYS_PATH
    for _key, _value in _PREVIOUS_TEST_ENV.items():
        if _value is None:
            os.environ.pop(_key, None)
        else:
            os.environ[_key] = _value


def _remove_test_home():
    shutil.rmtree(_TEST_HOME, ignore_errors=True)


atexit.register(_remove_test_home)


@pytest.fixture(autouse=True)
def _isolated_test_profile(monkeypatch):
    for key, value in _TEST_ENV.items():
        monkeypatch.setenv(key, value)


@pytest.fixture
def qt_app(_isolated_test_profile):
    return QApplication.instance() or QApplication([])


def _profile(name, account="synthetic", active=True):
    return app.SearchProfile(
        id=name,
        name=name,
        group="Test",
        account_name=account,
        active=active,
    )


def _worker(profiles, tmp_path):
    return app.GrabberWorker(
        profiles,
        [],
        app.DownloadSettings(enable_hash_check=False),
        tmp_path,
        [],
    )


class _FakeIMAP:
    def __init__(self):
        self.logout_calls = 0

    def logout(self):
        self.logout_calls += 1


def test_progress_counts_active_profiles_and_connection_failures_as_attempts(tmp_path, monkeypatch):
    profiles = [
        _profile("ready", "ready-account"),
        _profile("inactive", "offline-account", active=False),
        _profile("skipped-one", "offline-account"),
        _profile("skipped-two", "offline-account"),
    ]
    worker = _worker(profiles, tmp_path)
    conn = _FakeIMAP()
    connected = []
    processed = []
    events = []

    def connect(account_name):
        connected.append(account_name)
        return None if account_name == "offline-account" else conn

    monkeypatch.setattr(worker, "connect_imap", connect)
    monkeypatch.setattr(worker, "process_profile", lambda _c, profile, _s: processed.append(profile.name))
    worker.progress.connect(lambda current, total: events.append((current, total)))

    worker.run()

    assert worker.active_profile_count == 3
    assert connected == ["ready-account", "offline-account"]
    assert processed == ["ready"]
    assert events == [(0, 3), (1, 3), (2, 3), (3, 3)]
    assert conn.logout_calls == 1


def test_interruption_before_profile_does_not_count_it(tmp_path, monkeypatch):
    worker = _worker([_profile("first"), _profile("second")], tmp_path)
    conn = _FakeIMAP()
    events = []
    processed = []
    checks = iter([False, False, True])

    monkeypatch.setattr(worker, "connect_imap", lambda _account: conn)
    monkeypatch.setattr(worker, "process_profile", lambda _c, profile, _s: processed.append(profile.name))
    monkeypatch.setattr(worker, "isInterruptionRequested", lambda: next(checks, True))
    worker.progress.connect(lambda current, total: events.append((current, total)))

    worker.run()

    assert processed == ["first"]
    assert events == [(0, 2), (1, 2)]
    assert conn.logout_calls == 1


def test_connection_failure_skips_only_profiles_not_interrupted(tmp_path, monkeypatch):
    worker = _worker([_profile("first", "offline"), _profile("second", "offline")], tmp_path)
    events = []
    checks = iter([False, True])

    monkeypatch.setattr(worker, "connect_imap", lambda _account: None)
    monkeypatch.setattr(worker, "isInterruptionRequested", lambda: next(checks, True))
    worker.progress.connect(lambda current, total: events.append((current, total)))

    worker.run()

    assert events == [(0, 2)]


def test_profile_exception_counts_attempt_then_propagates(tmp_path, monkeypatch):
    worker = _worker([_profile("broken"), _profile("not-reached")], tmp_path)
    conn = _FakeIMAP()
    events = []
    processed = []

    monkeypatch.setattr(worker, "connect_imap", lambda _account: conn)

    def process(_conn, profile, _settings):
        processed.append(profile.name)
        raise RuntimeError("synthetic profile failure")

    monkeypatch.setattr(worker, "process_profile", process)
    worker.progress.connect(lambda current, total: events.append((current, total)))

    with pytest.raises(RuntimeError, match="synthetic profile failure"):
        worker.run()

    assert processed == ["broken"]
    assert events == [(0, 2), (1, 2)]


def test_zero_active_profiles_emit_determinate_zero_progress(tmp_path, monkeypatch):
    worker = _worker([_profile("inactive", active=False)], tmp_path)
    events = []
    monkeypatch.setattr(worker, "connect_imap", lambda _account: pytest.fail("inactive profile connected"))
    worker.progress.connect(lambda current, total: events.append((current, total)))

    worker.run()

    assert worker.active_profile_count == 0
    assert events == [(0, 0)]


class _ControlledWorker(app.QThread):
    log = app.Signal(str)
    progress = app.Signal(int, int)
    fail_next = False
    instances = []

    def __init__(self, profiles, *_args):
        super().__init__()
        self.active_profile_count = sum(1 for profile in profiles if profile.active)
        self.should_fail = type(self).fail_next
        type(self).fail_next = False
        self.entered = threading.Event()
        self.release = threading.Event()
        self.progress_events = []
        self.interrupted = False
        type(self).instances.append(self)

    def _emit_progress(self, current, total):
        self.progress_events.append((current, total))
        self.progress.emit(current, total)

    def run(self):
        total = self.active_profile_count
        self._emit_progress(0, total)
        if total:
            self._emit_progress(1, total)
        self.entered.set()
        self.release.wait(10)
        if self.isInterruptionRequested():
            self.interrupted = True
            self.log.emit("Synthetic scan aborted.")
            return
        if self.should_fail:
            self.log.emit("Synthetic profile failure.")
            raise RuntimeError("synthetic worker failure")
        if total:
            self._emit_progress(total, total)


def _window(monkeypatch, tmp_path, qt_app):
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "config_v1.json")
    monkeypatch.setattr(app, "DOCS_DB", tmp_path / "documents.json")
    window = app.MainWindow()
    window.accounts = [app.MailAccount("synthetic", "imap.example.org", "user@example.org")]
    window.profiles = [_profile("first"), _profile("second")]
    window.show()
    qt_app.processEvents()
    return window


def _finish_worker(worker, qt_app, interrupt=False):
    spy = QSignalSpy(worker.finished)
    if interrupt:
        worker.requestInterruption()
    worker.release.set()
    deadline = time.monotonic() + 5
    while worker.isRunning() and time.monotonic() < deadline:
        qt_app.processEvents()
        time.sleep(0.01)
    qt_app.processEvents()
    assert not worker.isRunning()
    assert spy.count() == 1


def test_gui_progress_is_connected_resets_once_on_failure_and_restarts(monkeypatch, tmp_path, qt_app):
    _ControlledWorker.instances.clear()
    _ControlledWorker.fail_next = False
    monkeypatch.setattr(app, "GrabberWorker", _ControlledWorker)
    window = _window(monkeypatch, tmp_path, qt_app)

    try:
        window.run_all()
        first = window.worker
        assert first.entered.wait(2)
        qt_app.processEvents()
        assert not window.btn_start.isEnabled()
        assert window.progress_bar.isVisible()
        assert window.progress_bar.minimum() == 0
        assert window.progress_bar.maximum() == 2
        assert window.progress_bar.value() == 1

        _finish_worker(first, qt_app)
        assert window.btn_start.isEnabled()
        assert window.btn_start.text() == app.UI_BTN_START
        assert not window.progress_bar.isVisible()
        assert window.progress_bar.value() == 0

        _ControlledWorker.fail_next = True
        window.run_all()
        second = window.worker
        assert second is not first
        assert second.entered.wait(2)
        qt_app.processEvents()
        assert window.progress_bar.isVisible()
        assert window.progress_bar.maximum() == 2
        assert window.progress_bar.value() == 1

        _finish_worker(second, qt_app)
        assert window.btn_start.isEnabled()
        assert window.btn_start.text() == app.UI_BTN_START
        assert not window.progress_bar.isVisible()
        assert window.progress_bar.value() == 0
    finally:
        for worker in _ControlledWorker.instances:
            worker.release.set()
            if worker.isRunning():
                worker.wait(5000)
        window.close()
        qt_app.processEvents()


def test_gui_zero_active_profiles_never_show_busy_bar(monkeypatch, tmp_path, qt_app):
    _ControlledWorker.instances.clear()
    _ControlledWorker.fail_next = False
    monkeypatch.setattr(app, "GrabberWorker", _ControlledWorker)
    window = _window(monkeypatch, tmp_path, qt_app)
    window.profiles = [_profile("inactive", active=False)]

    try:
        window.run_all()
        worker = window.worker
        assert worker.entered.wait(2)
        qt_app.processEvents()
        assert window.progress_bar.minimum() == 0
        assert window.progress_bar.maximum() == 1
        assert window.progress_bar.value() == 0
        assert not window.progress_bar.isVisible()
        _finish_worker(worker, qt_app)
        assert not window.progress_bar.isVisible()
    finally:
        for worker in _ControlledWorker.instances:
            worker.release.set()
            if worker.isRunning():
                worker.wait(5000)
        window.close()
        qt_app.processEvents()


def test_open_target_folder_button_uses_configured_path_without_creating_it(monkeypatch, tmp_path, qt_app):
    monkeypatch.setattr(app, "CONFIG_FILE", tmp_path / "config_v1.json")
    monkeypatch.setattr(app, "DOCS_DB", tmp_path / "documents.json")
    window = app.MainWindow()
    target = tmp_path / "not-created"
    window.base_path = str(target)
    opened = []
    monkeypatch.setattr(app, "QDesktopServices", SimpleNamespace(openUrl=lambda url: opened.append(url) or True))

    try:
        window.btn_open_base_folder.click()

        assert len(opened) == 1
        assert Path(opened[0].toLocalFile()) == target
        assert not target.exists()
    finally:
        window.close()
        qt_app.processEvents()

def test_progress_and_error_widgets_retranslate_without_resetting_running_worker(monkeypatch, tmp_path, qt_app):
    _ControlledWorker.instances.clear()
    _ControlledWorker.fail_next = False
    monkeypatch.setattr(app, "GrabberWorker", _ControlledWorker)
    window = _window(monkeypatch, tmp_path, qt_app)

    try:
        window.run_all()
        worker = window.worker
        assert worker.entered.wait(2)
        qt_app.processEvents()
        assert worker.isRunning()
        assert window.progress_label.isVisible()
        assert window.progress_bar.isVisible()
        assert (window.progress_bar.minimum(), window.progress_bar.maximum(), window.progress_bar.value()) == (0, 2, 1)

        account_error = app.AccountIdentityError(
            "synthetic account identity error", "ERR_ACCOUNT_NAME_EMPTY", index=1
        )
        window._set_account_identity_error(str(account_error), account_error)

        for language in ("de", "en", "es", "zh", "ja", "ru"):
            window.set_ui_language(language)
            qt_app.processEvents()
            tr = window.translator
            assert window.progress_label.text() == tr.t("UI_LABEL_SCAN_PROGRESS")
            assert window.progress_label.toolTip() == tr.t("TT_SCAN_PROGRESS")
            assert window.progress_label.accessibleName() == tr.t("ACC_SCAN_PROGRESS")
            assert window.progress_bar.toolTip() == tr.t("TT_SCAN_PROGRESS")
            assert window.progress_bar.accessibleName() == tr.t("ACC_SCAN_PROGRESS")
            assert window.progress_bar.accessibleDescription() == tr.t("ACC_DESC_SCAN_PROGRESS")
            assert window.btn_open_base_folder.text() == tr.t("UI_BTN_OPEN_BASE_FOLDER")
            assert window.btn_open_base_folder.toolTip() == tr.t("TT_BTN_OPEN_BASE_FOLDER")
            assert window.btn_open_base_folder.accessibleName() == tr.t("ACC_BTN_OPEN_BASE_FOLDER")
            assert window.btn_open_base_folder.accessibleDescription() == tr.t("ACC_DESC_BTN_OPEN_BASE_FOLDER")
            assert window.btn_start.text() == tr.t("UI_BTN_RUNNING")
            assert window.progress_label.isVisible()
            assert window.progress_bar.isVisible()
            assert (window.progress_bar.minimum(), window.progress_bar.maximum(), window.progress_bar.value()) == (0, 2, 1)
            assert window.account_identity_notice.isVisible()
            assert window.account_identity_notice.text() == tr.t(
                "UI_ACCOUNT_IDENTITY_BLOCKED", error=account_error.translated(tr)
            )
            assert window.lbl_scheduler_status.text() == tr.t("UI_SCHEDULER_IDENTITY_BLOCKED")
            assert not window.btn_start.isEnabled()

        worker.should_fail = True
        _finish_worker(worker, qt_app)
        assert "Synthetic profile failure." in window.log.toPlainText()
        assert not window.progress_bar.isVisible()
        assert window.progress_bar.value() == 0
        assert window.btn_start.text() == window.translator.t("UI_BTN_START")
        assert not window.btn_start.isEnabled()
        assert window.account_identity_notice.isVisible()
        assert window.account_identity_notice.text() == window.translator.t(
            "UI_ACCOUNT_IDENTITY_BLOCKED", error=account_error.translated(window.translator)
        )
    finally:
        for active_worker in _ControlledWorker.instances:
            active_worker.release.set()
            if active_worker.isRunning():
                active_worker.wait(5000)
        window.close()
        qt_app.processEvents()


def test_gui_abort_does_not_force_progress_complete_and_native_finished_resets(monkeypatch, tmp_path, qt_app):
    _ControlledWorker.instances.clear()
    _ControlledWorker.fail_next = False
    monkeypatch.setattr(app, "GrabberWorker", _ControlledWorker)
    window = _window(monkeypatch, tmp_path, qt_app)

    try:
        window.run_all()
        worker = window.worker
        assert worker.entered.wait(2)
        qt_app.processEvents()
        assert worker.progress_events == [(0, 2), (1, 2)]
        assert window.progress_bar.value() == 1

        _finish_worker(worker, qt_app, interrupt=True)

        assert worker.interrupted
        assert worker.progress_events == [(0, 2), (1, 2)]
        assert not window.progress_bar.isVisible()
        assert window.progress_bar.value() == 0
        assert window.btn_start.isEnabled()
        assert window.btn_start.text() == window.translator.t("UI_BTN_START")
        assert "Synthetic scan aborted." in window.log.toPlainText()
    finally:
        for active_worker in _ControlledWorker.instances:
            active_worker.release.set()
            if active_worker.isRunning():
                active_worker.wait(5000)
        window.close()
        qt_app.processEvents()
