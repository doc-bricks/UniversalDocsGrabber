"""Tests for GrabberWorker._auto_categorize."""

import os
import sys
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).parent.parent))

from PySide6.QtWidgets import QApplication

import UniversalDocsGrabberV1 as app

_qt_app = QApplication.instance() or QApplication(sys.argv)


def _worker(tmp_path, settings: app.DownloadSettings) -> app.GrabberWorker:
    return app.GrabberWorker([], [], settings, tmp_path, [])


# ---------------------------------------------------------------------------
# short-circuit
# ---------------------------------------------------------------------------

def test_returns_none_when_auto_categorize_disabled(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=False))
    assert worker._auto_categorize("billing@example.org", "Rechnung 123", worker.global_settings) is None


# ---------------------------------------------------------------------------
# custom rules
# ---------------------------------------------------------------------------

def test_custom_rule_matches_subject(tmp_path):
    settings = app.DownloadSettings(
        auto_categorize=True,
        category_rules=[{"keyword": "premium", "folder": "Premium", "match": "subject"}],
    )
    worker = _worker(tmp_path, settings)
    result = worker._auto_categorize("no-match@example.org", "Premium subscription renewal", worker.global_settings)
    assert result == "Premium"


def test_custom_rule_does_not_match_wrong_field(tmp_path):
    """match='sender' must not fire when keyword only appears in subject."""
    settings = app.DownloadSettings(
        auto_categorize=True,
        category_rules=[{"keyword": "premium", "folder": "Premium", "match": "sender"}],
    )
    worker = _worker(tmp_path, settings)
    result = worker._auto_categorize("noreply@example.org", "Premium subscription", worker.global_settings)
    assert result is None


def test_custom_rule_matches_sender(tmp_path):
    settings = app.DownloadSettings(
        auto_categorize=True,
        category_rules=[{"keyword": "amazon", "folder": "Amazon", "match": "sender"}],
    )
    worker = _worker(tmp_path, settings)
    result = worker._auto_categorize("shipment@amazon.de", "Your order has shipped", worker.global_settings)
    assert result == "Amazon"


def test_custom_rule_match_both_fires_on_subject(tmp_path):
    settings = app.DownloadSettings(
        auto_categorize=True,
        category_rules=[{"keyword": "steuer", "folder": "Steuer2026", "match": "both"}],
    )
    worker = _worker(tmp_path, settings)
    result = worker._auto_categorize("elster@example.org", "Steuerabrechnung 2026", worker.global_settings)
    assert result == "Steuer2026"


def test_custom_rule_wins_over_default_rule(tmp_path):
    """Custom 'rechnung' rule must win over the default 'Rechnungen' rule."""
    settings = app.DownloadSettings(
        auto_categorize=True,
        category_rules=[{"keyword": "rechnung", "folder": "MeineRechnungen", "match": "subject"}],
    )
    worker = _worker(tmp_path, settings)
    result = worker._auto_categorize("bills@example.org", "Rechnung #42", worker.global_settings)
    assert result == "MeineRechnungen"


# ---------------------------------------------------------------------------
# default rules
# ---------------------------------------------------------------------------

def test_default_rule_rechnung_german(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=True))
    assert worker._auto_categorize("x@x.org", "Rechnung für Mai 2026", worker.global_settings) == "Rechnungen"


def test_default_rule_invoice_english(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=True))
    assert worker._auto_categorize("billing@co.com", "Invoice #0042", worker.global_settings) == "Rechnungen"


def test_default_rule_versand(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=True))
    assert worker._auto_categorize("x@x.org", "Sendung wurde versendet", worker.global_settings) == "Versand"


def test_default_rule_vertrag_with_umlaut_folder(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=True))
    result = worker._auto_categorize("x@x.org", "Ihr Vertrag wurde verlängert", worker.global_settings)
    assert result == "Verträge"


def test_default_rule_kuendigung_with_umlaut_folder(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=True))
    result = worker._auto_categorize("x@x.org", "Kuendigung bestätigt", worker.global_settings)
    assert result == "Kündigungen"


def test_default_rule_steuer(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=True))
    assert worker._auto_categorize("x@x.org", "Steuerbescheid 2025", worker.global_settings) == "Steuer"


def test_default_rule_versicherung(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=True))
    assert worker._auto_categorize("x@x.org", "Versicherungsschein aktualisiert", worker.global_settings) == "Versicherung"


def test_default_rule_bank(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=True))
    assert worker._auto_categorize("x@x.org", "Kontoauszug August 2026", worker.global_settings) == "Bank"


def test_no_match_returns_none(tmp_path):
    worker = _worker(tmp_path, app.DownloadSettings(auto_categorize=True))
    result = worker._auto_categorize("friend@example.org", "Weekend plans", worker.global_settings)
    assert result is None
