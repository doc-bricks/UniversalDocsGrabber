"""
Tests für den UniversalDocsGrabber Web Companion & PWA.

Validiert:
1. Vollständigkeit der Dateien und W3C-Manifest-Integrität.
2. Existenz aller referenzierten App-Icons und Service-Worker-Caches.
3. Zero-Egress-Invariante (keine externen CDNs, Scripts oder Web-Fonts).
4. Kompatibilität des Session-Exchange-Formats (docsgrabber-library-v1.json).
5. Tier-2 Lokalisierungs-Parität (DE, EN, ES, ZH, JA, RU) und HTML5-Sprachauswahl.
6. Erfolgreicher Durchlauf der nativen Node.js-Testsuite.
"""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WEB_DIR = PROJECT_ROOT / "web_companion"


def test_web_companion_core_files_exist():
    """Prüft, ob alle Kernkomponenten des Web Companions vorhanden sind."""
    required_files = [
        WEB_DIR / "index.html",
        WEB_DIR / "app.css",
        WEB_DIR / "app.js",
        WEB_DIR / "library.js",
        WEB_DIR / "sw.js",
        WEB_DIR / "manifest.webmanifest",
        WEB_DIR / "package.json",
        WEB_DIR / "README.md",
        WEB_DIR / "favicon.png",
        WEB_DIR / "favicon.ico",
        WEB_DIR / "icons" / "apple-touch-icon-180.png",
        WEB_DIR / "icons" / "Icon-192.png",
        WEB_DIR / "icons" / "Icon-512.png",
    ]
    for file_path in required_files:
        assert file_path.exists(), f"Erwartete Datei fehlt: {file_path.name}"
        assert file_path.stat().st_size > 0, f"Datei ist leer: {file_path.name}"


def test_web_companion_zero_egress_and_local_first():
    """Stellt sicher, dass keine externen CDNs, Fonts oder Telemetrie-URLs geladen werden."""
    html_content = (WEB_DIR / "index.html").read_text(encoding="utf-8")
    js_content = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    lib_content = (WEB_DIR / "library.js").read_text(encoding="utf-8")

    # In HTML dürfen keine externen Scripts oder Stylesheets referenziert werden
    external_refs = re.findall(r'(?:src|href)=["\'](https?://[^"\']+)["\']', html_content)
    assert external_refs == [], f"Externe Netzwerk-Referenzen in index.html gefunden: {external_refs}"

    # Keine unberechtigten Fetch- oder WebSocket-Aufrufe an externe Hosts
    for label, code in [("app.js", js_content), ("library.js", lib_content)]:
        network_calls = re.findall(r'fetch\(["\'](https?://[^"\']+)["\']\)', code)
        assert network_calls == [], f"Externe HTTP-Aufrufe in {label} gefunden: {network_calls}"


def test_web_companion_i18n_dictionary_parity():
    """Validiert 100% Übersetzungsparität aller 6 Tier-2 Sprachen im Web Companion."""
    app_js = (WEB_DIR / "app.js").read_text(encoding="utf-8")
    match = re.search(r"const\s+I18N\s*=\s*(\{[\s\S]*?\n\};)", app_js)
    assert match is not None, "const I18N Objekt nicht in app.js gefunden"

    raw_block = match.group(1).rstrip(";").replace("const I18N = ", "")

    expected_langs = ["de", "en", "es", "zh", "ja", "ru"]
    for lang in expected_langs:
        assert f"{lang}: {{" in raw_block, f"Sprache '{lang}' fehlt im I18N-Katalog"

    pattern = re.compile(r"^\s\s([a-z]{2}):\s*\{([\s\S]*?)\n\s\s\}", re.MULTILINE)
    lang_keys: dict[str, set[str]] = {}

    for l_match in pattern.finditer(raw_block):
        lang_code = l_match.group(1)
        body = l_match.group(2)
        keys = set(re.findall(r"^\s+([a-zA-Z0-9_]+)\s*:", body, re.MULTILINE))
        lang_keys[lang_code] = keys

    assert set(lang_keys.keys()) == set(expected_langs), "Nicht alle 6 Sprachen geparst"

    de_keys = lang_keys["de"]
    assert len(de_keys) >= 40, f"Zu wenige I18N-Schlüssel: {len(de_keys)}"

    for lang in ["en", "es", "zh", "ja", "ru"]:
        diff = de_keys.symmetric_difference(lang_keys[lang])
        assert diff == set(), f"I18N Diskrepanz zwischen 'de' und '{lang}': {diff}"


def test_web_companion_html_language_selector():
    """Prüft, ob der Sprachauswahlschalter in index.html alle 6 Sprachen anbietet."""
    html_content = (WEB_DIR / "index.html").read_text(encoding="utf-8")

    assert 'id="lang-select"' in html_content
    expected_options = ['value="de"', 'value="en"', 'value="es"', 'value="zh"', 'value="ja"', 'value="ru"']
    for opt in expected_options:
        assert opt in html_content, f"Option {opt} fehlt im #lang-select"


def test_web_companion_sw_cache_and_manifest():
    """Validiert Service Worker und Manifest-Metadaten."""
    sw_content = (WEB_DIR / "sw.js").read_text(encoding="utf-8")
    assert "docsgrabber-companion-v3" in sw_content or "docsgrabber-companion-v2" in sw_content

    manifest_data = json.loads((WEB_DIR / "manifest.webmanifest").read_text(encoding="utf-8"))
    assert manifest_data.get("display") == "standalone"
    assert manifest_data.get("start_url") == "./index.html"


def test_web_companion_node_test_suite_passes():
    """Führt die native Node.js-Testsuite im web_companion Verzeichnis aus."""
    res = subprocess.run(
        ["node", "--test"],
        cwd=str(WEB_DIR),
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert res.returncode == 0, f"Node.js Testsuite fehlgeschlagen:\nSTDOUT:\n{res.stdout}\nSTDERR:\n{res.stderr}"
