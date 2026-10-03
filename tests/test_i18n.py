# -*- coding: utf-8 -*-
"""
Vertragstests: Policy P-006 Tier-2 6-Sprachen-I18N-Standard (UniversalDocsGrabber).
===================================================================================
Verifiziert:
1. locales/translations.json Integrität und 100% Schlüssel-Parität über alle 6 Sprachen.
2. Deterministische 4-Stufen-Fallback-Kette (target -> en -> de -> key).
3. Parameter-Interpolation via t(key, **kwargs) und Fehlertoleranz.
4. TranslationSystem-Klassenmethoden und Metadaten-Mappings.
5. manage_translations.py --check Subprozess-Validierung (Exit 0).
6. manage_translations.py --stats Subprozess-Validierung (Exit 0).
7. Erhalt echter deutscher Umlaute (ä, ö, ü, Ä, Ö, Ü, ß) in allen Schlüsseln und Werten.
8. Erhalt echter spanischer Diakritika (á, é, í, ó, ú, ñ, ¿, ¡) im Katalog.
9. Konsistenz der nativen Sprachnamen (Deutsch, English, Español, 简体中文, 日本語, Русский).
10. Systemsprachenerkennung via detect_system_language().
11. UI-Sprachumschaltung und dynamische Aktualisierung in MainWindow (retranslate_ui).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from PySide6.QtWidgets import QApplication

from translator import (
    TranslationSystem,
    detect_system_language,
    get_translator,
    t,
)
from UniversalDocsGrabberV1 import MainWindow, SearchProfile


@pytest.fixture(scope="module")
def qapp():
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


def test_supported_languages_contract():
    """Prüft, ob alle 6 P-006 Standard-Sprachen deklariert und abrufbar sind."""
    expected = ("de", "en", "es", "zh", "ja", "ru")
    assert TranslationSystem.SUPPORTED_LANGUAGES == expected
    assert TranslationSystem.FALLBACK_LANGUAGES == ("en", "de")
    assert TranslationSystem.DEFAULT_LANGUAGE == "de"
    assert TranslationSystem.get_supported_languages() == list(expected)


def test_language_names_and_display_mappings():
    """Prüft die Vollständigkeit und native Schreibweise aller 6 Sprachen."""
    names = TranslationSystem.get_language_names()
    assert names["de"] == "Deutsch"
    assert names["en"] == "English"
    assert names["es"] == "Español"
    assert names["zh"] == "简体中文"
    assert names["ja"] == "日本語"
    assert names["ru"] == "Русский"

    display_names = TranslationSystem.get_language_display_names()
    for lang in TranslationSystem.SUPPORTED_LANGUAGES:
        assert lang in display_names
        assert f"({lang})" in display_names[lang]


def test_translations_json_file_validity_and_parity():
    """Prüft locales/translations.json auf Existenz, Mindestgröße und 100% Parität."""
    proj_dir = Path(__file__).resolve().parent.parent
    trans_file = proj_dir / "locales" / "translations.json"
    assert trans_file.is_file(), f"{trans_file} muss als reguläre Datei existieren"

    with open(trans_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    assert isinstance(data, dict)
    assert len(data) >= 100, f"Mindestens 100 Schlüssel erwartet, {len(data)} gefunden"

    for key, val in data.items():
        assert isinstance(val, dict), f"Eintrag für {key} muss ein Dict sein"
        for lang in TranslationSystem.SUPPORTED_LANGUAGES:
            assert lang in val, f"Sprache '{lang}' fehlt in Schlüssel '{key}'"
            entry_str = val[lang]
            assert isinstance(entry_str, str) and entry_str.strip(), (
                f"Leere Übersetzung für Schlüssel '{key}' in Sprache '{lang}'"
            )


def test_deterministic_fallback_chain(tmp_path):
    """Prüft die 4-stufige Fallback-Kette: target -> en -> de -> key."""
    locales_dir = tmp_path / "locales"
    locales_dir.mkdir(parents=True)
    custom_json = locales_dir / "translations.json"

    dummy_catalog = {
        "FullKey": {
            "de": "Starten",
            "en": "Start",
            "es": "Iniciar",
            "zh": "开始",
            "ja": "開始",
            "ru": "Старт",
        },
        "MissingSpanish": {
            "de": "Einstellungen",
            "en": "Settings",
            "es": "",
            "zh": "",
            "ja": "",
            "ru": "",
        },
        "OnlyGerman": {
            "de": "NurDeutsch",
            "en": "",
            "es": "",
            "zh": "",
            "ja": "",
            "ru": "",
        },
    }
    with open(custom_json, "w", encoding="utf-8") as f:
        json.dump(dummy_catalog, f, indent=2, ensure_ascii=False)

    ts = TranslationSystem(default_lang="es", app_dir=tmp_path)

    # 1. Voller Schlüssel in Zielsprache 'es'
    assert ts.t("FullKey") == "Iniciar"

    # 2. 'es' fehlt -> Fallback auf 'en'
    assert ts.t("MissingSpanish") == "Settings"

    # 3. 'es' und 'en' fehlen -> Fallback auf 'de'
    assert ts.t("OnlyGerman") == "NurDeutsch"

    # 4. Schlüssel existiert überhaupt nicht -> Fallback auf key selbst
    assert ts.t("CompletelyUnknownKey") == "CompletelyUnknownKey"


def test_param_interpolation_and_error_tolerance():
    """Prüft kwargs-Interpolation und Absicherung gegen Formatierungsfehler."""
    ts = TranslationSystem("de")

    # Gültige Interpolation
    res_de = ts.t("UI_SCHEDULER_ACTIVE", interval=30)
    assert "30" in res_de
    assert "Scheduler" in res_de

    # Umschaltung auf Englisch
    ts.set_language("en")
    res_en = ts.t("UI_SCHEDULER_ACTIVE", interval=30)
    assert "30" in res_en
    assert "min." in res_en

    # Fehlertoleranz bei falschem Formatierungs-Aufruf
    res_err = ts.t("UI_SCHEDULER_ACTIVE", wrong_param=123)
    assert "interval" in res_err or "Scheduler" in res_err


def test_manage_translations_cli_check():
    """Führt manage_translations.py --check im Subprozess aus und erwartet Exit 0."""
    proj_dir = Path(__file__).resolve().parent.parent
    script_path = proj_dir / "manage_translations.py"
    assert script_path.is_file()

    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, str(script_path), "--check"],
        cwd=str(proj_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=15,
    )
    assert result.returncode == 0, f"CLI-Check fehlgeschlagen:\n{result.stderr}\n{result.stdout}"
    assert "100% Parität über alle 6 Sprachen" in result.stdout


def test_manage_translations_cli_stats():
    """Führt manage_translations.py --stats im Subprozess aus und erwartet Exit 0."""
    proj_dir = Path(__file__).resolve().parent.parent
    script_path = proj_dir / "manage_translations.py"
    assert script_path.is_file()

    env = dict(os.environ, PYTHONIOENCODING="utf-8")
    result = subprocess.run(
        [sys.executable, str(script_path), "--stats"],
        cwd=str(proj_dir),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        env=env,
        timeout=15,
    )
    assert result.returncode == 0, f"CLI-Stats fehlgeschlagen:\n{result.stderr}\n{result.stdout}"
    assert "100.0%" in result.stdout


def test_german_umlauts_preservation():
    """Prüft, ob deutsche Umlaute in translations.json echt und unbeschädigt vorliegen."""
    proj_dir = Path(__file__).resolve().parent.parent
    trans_file = proj_dir / "locales" / "translations.json"
    with open(trans_file, "r", encoding="utf-8") as f:
        content = f.read()

    for char in ("ä", "ö", "ü", "Ä", "Ö", "Ü", "ß"):
        assert char in content, f"Umlaut '{char}' fehlt im Übersetzungskatalog"


def test_spanish_diacritics_preservation():
    """Prüft, ob spanische Diakritika in translations.json echt vorliegen."""
    proj_dir = Path(__file__).resolve().parent.parent
    trans_file = proj_dir / "locales" / "translations.json"
    with open(trans_file, "r", encoding="utf-8") as f:
        content = f.read()

    for char in ("á", "é", "í", "ó", "ú", "ñ", "¿", "¡"):
        assert char in content, f"Spanisches Zeichen '{char}' fehlt im Übersetzungskatalog"


def test_system_language_detection():
    """Prüft, ob detect_system_language() einen gültigen 2-Letter-Code zurückliefert."""
    detected = detect_system_language()
    assert detected in TranslationSystem.SUPPORTED_LANGUAGES


def test_global_helper_functions():
    """Prüft get_translator() und t() Helferfunktionen."""
    ts = get_translator("de")
    assert ts.get_language() == "de"
    val = t("UI_TAB_DOCS")
    assert "Dokumente" in val


def test_mainwindow_ui_language_switch_and_retranslate(qapp, tmp_path, monkeypatch):
    """Prüft dynamischen Sprachwechsel im MainWindow via set_ui_language."""
    test_config = tmp_path / "config_v1.json"
    test_docs = tmp_path / "documents.json"
    monkeypatch.setattr("UniversalDocsGrabberV1.CONFIG_FILE", test_config)
    monkeypatch.setattr("UniversalDocsGrabberV1.DOCS_DB", test_docs)

    win = MainWindow()
    assert win.language == "de"
    assert "Dokumente" in win.tabs.tabText(1)
    assert "Einstellungen" in win.tabs.tabText(2)

    # Wechsel auf Spanisch
    win.set_ui_language("es")
    assert win.language == "es"
    assert "Documentos" in win.tabs.tabText(1)
    assert "Configuración" in win.tabs.tabText(2)

    # Wechsel auf Englisch
    win.set_ui_language("en")
    assert win.language == "en"
    assert "Documents" in win.tabs.tabText(1)
    assert "Settings" in win.tabs.tabText(2)

    # Wechsel auf Chinesisch
    win.set_ui_language("zh")
    assert win.language == "zh"
    assert "文档" in win.tabs.tabText(1)
    assert "设置" in win.tabs.tabText(2)

    # Wechsel auf Japanisch
    win.set_ui_language("ja")
    assert win.language == "ja"
    assert "ドキュメント" in win.tabs.tabText(1)
    assert "設定" in win.tabs.tabText(2)

    # Wechsel auf Russisch
    win.set_ui_language("ru")
    assert win.language == "ru"
    assert "Документы" in win.tabs.tabText(1)
    assert "Настройки" in win.tabs.tabText(2)

    # Wechsel zurück auf Deutsch
    win.set_ui_language("de")
    assert win.language == "de"
    assert "Dokumente" in win.tabs.tabText(1)
    assert "Einstellungen" in win.tabs.tabText(2)

    win.close()


def test_saved_language_and_profiles_survive_reload(qapp, tmp_path, monkeypatch):
    config_path = tmp_path / "config_v1.json"
    docs_path = tmp_path / "documents.json"
    monkeypatch.setattr("UniversalDocsGrabberV1.CONFIG_FILE", config_path)
    monkeypatch.setattr("UniversalDocsGrabberV1.DOCS_DB", docs_path)

    first = MainWindow()
    first.profiles = [
        SearchProfile(
            id="profile-i18n-persist",
            name="Persisted profile",
            group="Synthetic",
            account_name="",
            active=False,
        )
    ]
    assert first.save_config() is True

    first.set_ui_language("es")
    saved = json.loads(config_path.read_text(encoding="utf-8"))
    assert saved["language"] == "es"
    assert saved["profiles"][0]["id"] == "profile-i18n-persist"
    assert saved["profiles"][0]["active"] is False
    first.close()

    restored = MainWindow()
    assert restored.language == "es"
    assert restored.translator.get_language() == "es"
    assert restored.cb_language.currentData() == "es"
    assert restored.tabs.tabText(1) == restored.translator.t("UI_TAB_DOCS")
    assert [(profile.id, profile.name, profile.active) for profile in restored.profiles] == [
        ("profile-i18n-persist", "Persisted profile", False)
    ]
    restored.close()


def test_readme_es_parity_and_anchors():
    """Prüft README_es.md auf Existenz, 18 Abschnitte und reziproke sec-01..sec-18 Anker."""
    proj_dir = Path(__file__).resolve().parent.parent
    readme_es_path = proj_dir / "README_es.md"
    assert readme_es_path.is_file(), "README_es.md muss als reguläre Datei existieren"

    readme_es = readme_es_path.read_text(encoding="utf-8")
    readme_en = (proj_dir / "README.md").read_text(encoding="utf-8")
    readme_de = (proj_dir / "README-DE.md").read_text(encoding="utf-8")

    # Alle 18 sec-XX Anker müssen in allen 3 READMEs vorhanden sein
    for i in range(1, 19):
        anchor = f'<a id="sec-{i:02d}"></a>'
        assert anchor in readme_es, f"Anker {anchor} fehlt in README_es.md"
        assert anchor in readme_en, f"Anker {anchor} fehlt in README.md"
        assert anchor in readme_de, f"Anker {anchor} fehlt in README-DE.md"

    # Dreisprachige Sprachleiste
    for text in (readme_en, readme_de, readme_es):
        assert "README.md" in text
        assert "README-DE.md" in text
        assert "README_es.md" in text


def test_readme_es_invariants_and_statutory_notice():
    """Prüft Invarianten und § 521 BGB Haftungsausschluss in README_es.md."""
    proj_dir = Path(__file__).resolve().parent.parent
    readme_es = (proj_dir / "README_es.md").read_text(encoding="utf-8")

    for i in range(1, 11):
        assert "INV-" in readme_es and f"{i:02d}" in readme_es

    assert "521 BGB" in readme_es
    assert "Gefälligkeitsrecht" in readme_es
    assert "48h" in readme_es or "48 horas" in readme_es
    assert "docsgrabber-library-v1.json" in readme_es
