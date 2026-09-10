"""
Store-Readiness Preflight Checker für UniversalDocsGrabber.
Prüft alle Windows Store Release Readiness Artefakte auf Vollständigkeit, Konsistenz und Richtlinienkonformität.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BANNED_TRADEMARKS = {"windows", "microsoft", "google", "gmail", "apple", "adobe", "outlook"}


def check_store_readiness() -> tuple[list[str], list[str]]:
    """Führt alle Preflight-Prüfungen für die Windows Store Release Readiness durch.

    Returns:
        tuple[list[str], list[str]]: (passed_checks, findings)
    """
    passed: list[str] = []
    findings: list[str] = []

    # 1. store_package.json
    pkg_file = PROJECT_ROOT / "store_package.json"
    if not pkg_file.exists():
        findings.append("store_package.json fehlt im Projektroot.")
    else:
        try:
            data = json.loads(pkg_file.read_text(encoding="utf-8"))
            req_fields = [
                "app_name", "identity_name", "publisher", "publisher_display",
                "version", "description", "executable", "capabilities", "category",
                "age_rating", "privacy_url", "support_url"
            ]
            missing = [f for f in req_fields if f not in data or not data[f]]
            if missing:
                findings.append(f"store_package.json: Fehlende Pflichtfelder: {missing}")
            else:
                passed.append("store_package.json Pflichtfelder vollständig")

            if not data.get("publisher", "").startswith("CN="):
                findings.append("store_package.json: 'publisher' muss mit 'CN=' beginnen.")
            else:
                passed.append("store_package.json Publisher-DN hat CN=-Format")

            if data.get("executable") != "UniversalDocsGrabber.exe":
                findings.append(f"store_package.json: Executable ist '{data.get('executable')}', erwartet 'UniversalDocsGrabber.exe'")
            else:
                passed.append("store_package.json Executable ist UniversalDocsGrabber.exe")

            if not re.match(r"^\d+\.\d+\.\d+\.\d+$", data.get("version", "")):
                findings.append(f"store_package.json: Version '{data.get('version')}' ist kein 4-teiliger Version-String.")
            else:
                passed.append("store_package.json Version-Format (4-teilig) OK")

            if "github.com" not in data.get("privacy_url", ""):
                findings.append("store_package.json: 'privacy_url' muss auf GitHub verweisen.")
            else:
                passed.append("store_package.json privacy_url verweist auf GitHub")

            if "github.com" not in data.get("support_url", ""):
                findings.append("store_package.json: 'support_url' muss auf GitHub verweisen.")
            else:
                passed.append("store_package.json support_url verweist auf GitHub")

        except Exception as err:
            findings.append(f"store_package.json konnte nicht gelesen/geparst werden: {err}")

    # 2. Store-Dokumente
    doc_files = {
        "STORE_LISTING.md": "Store Listing (DE/EN)",
        "PRIVACY.md": "Datenschutzerklärung",
        "SUPPORT.md": "Support-Dokumentation",
        "WINDOWS_STORE_PREP.md": "Windows Store Vorbereitungsdoku",
    }
    for filename, label in doc_files.items():
        path = PROJECT_ROOT / filename
        if not path.exists():
            findings.append(f"{filename} ({label}) fehlt.")
        elif path.stat().st_size < 100:
            findings.append(f"{filename} ist zu kurz (< 100 Bytes).")
        else:
            passed.append(f"{filename} ({label}) vorhanden und befüllt")

    # 3. Keyword-Richtlinie 10.1.3 in STORE_LISTING.md
    listing_path = PROJECT_ROOT / "STORE_LISTING.md"
    if listing_path.exists():
        content = listing_path.read_text(encoding="utf-8")
        de_match = re.search(r"## Deutsch[\s\S]*?### Suchbegriffe[^\n]*\n([\s\S]*?)(?=---|\Z)", content)
        en_match = re.search(r"## English[\s\S]*?### Search Keywords[^\n]*\n([\s\S]*?)(?=\Z)", content)

        for lang, match in [("DE", de_match), ("EN", en_match)]:
            if not match:
                findings.append(f"STORE_LISTING.md: Keine Keywords für {lang} gefunden.")
                continue
            lines = [line.strip() for line in match.group(1).strip().splitlines() if line.strip()]
            keywords = []
            for line in lines:
                m = re.match(r"^\d+\.\s*(.+)$", line)
                if m:
                    keywords.append(m.group(1).strip().lower())

            if len(keywords) > 7:
                findings.append(f"STORE_LISTING.md ({lang}): Zu viele Keywords ({len(keywords)} > 7, Richtlinie 10.1.3 verletzt).")
            elif len(keywords) == 0:
                findings.append(f"STORE_LISTING.md ({lang}): Keine Keywords extrahiert.")
            else:
                passed.append(f"STORE_LISTING.md ({lang}): {len(keywords)}/7 Keywords (Richtlinie 10.1.3 eingehalten)")

            trademark_hits = [kw for kw in keywords if kw in BANNED_TRADEMARKS]
            if trademark_hits:
                findings.append(f"STORE_LISTING.md ({lang}): Markenbegriffe in Keywords gefunden: {trademark_hits}")
            else:
                passed.append(f"STORE_LISTING.md ({lang}): Keine geschützten Markenbegriffe in Keywords")

    return passed, findings


def main() -> int:
    passed, findings = check_store_readiness()
    print("=== STORE-READINESS PREFLIGHT REPORT ===")
    for p in passed:
        print(f"  [OK] {p}")
    if findings:
        print("\n=== GEFUNDENE PROBLEME ===")
        for f in findings:
            print(f"  [FEHLER] {f}")
        return 1
    print("\n[ERFOLG] Alle Store-Readiness-Prüfungen bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
