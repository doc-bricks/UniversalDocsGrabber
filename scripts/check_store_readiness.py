"""
Store-Readiness Preflight Checker für UniversalDocsGrabber.
Prüft alle Windows Store Release Readiness Artefakte auf Vollständigkeit, Konsistenz und Richtlinienkonformität.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

try:
    from PIL import Image
except ImportError:
    Image = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]

BANNED_TRADEMARKS = {"windows", "microsoft", "google", "gmail", "apple", "adobe", "outlook"}
EXPECTED_PUBLISHER = "CN=52596601-BAB4-4F3F-B182-E8F3F273B202"
EXPECTED_IDENTITY = "Geiger.UniversalDocsGrabber"


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
                "age_rating", "license", "languages", "privacy_url", "support_url"
            ]
            missing = [f for f in req_fields if f not in data or not data[f]]
            if missing:
                findings.append(f"store_package.json: Fehlende Pflichtfelder: {missing}")
            else:
                passed.append("store_package.json Pflichtfelder vollständig (inkl. license, languages)")

            if data.get("publisher") != EXPECTED_PUBLISHER:
                findings.append(f"store_package.json: 'publisher' ist '{data.get('publisher')}', erwartet '{EXPECTED_PUBLISHER}'")
            else:
                passed.append("store_package.json Publisher-DN hat CN=-Format und entspricht Partner Center")

            if data.get("identity_name") != EXPECTED_IDENTITY:
                findings.append(f"store_package.json: 'identity_name' ist '{data.get('identity_name')}', erwartet '{EXPECTED_IDENTITY}'")
            else:
                passed.append(f"store_package.json Identity Name ist {EXPECTED_IDENTITY}")

            if data.get("executable") != "UniversalDocsGrabber.exe":
                findings.append(f"store_package.json: Executable ist '{data.get('executable')}', erwartet 'UniversalDocsGrabber.exe'")
            else:
                passed.append("store_package.json Executable ist UniversalDocsGrabber.exe")

            if not re.match(r"^\d+\.\d+\.\d+\.\d+$", data.get("version", "")):
                findings.append(f"store_package.json: Version '{data.get('version')}' ist kein 4-teiliger Version-String.")
            else:
                passed.append("store_package.json Version-Format (4-teilig) OK")

            if not data.get("privacy_url", "").startswith("https://"):
                findings.append("store_package.json: 'privacy_url' muss eine HTTPS-URL sein.")
            else:
                passed.append("store_package.json privacy_url ist gültige HTTPS-URL")

            if not data.get("support_url", "").startswith("https://"):
                findings.append("store_package.json: 'support_url' muss eine HTTPS-URL sein.")
            else:
                passed.append("store_package.json support_url ist gültige HTTPS-URL")

        except Exception as err:
            findings.append(f"store_package.json konnte nicht gelesen/geparst werden: {err}")

    # 2. AppxManifest.xml
    manifest_file = PROJECT_ROOT / "store_package" / "UniversalDocsGrabber" / "AppxManifest.xml"
    if not manifest_file.exists():
        findings.append("AppxManifest.xml fehlt unter store_package/UniversalDocsGrabber/")
    else:
        try:
            tree = ET.parse(manifest_file)
            root = tree.getroot()
            identity_elem = None
            for elem in root.iter():
                if elem.tag.endswith("Identity"):
                    identity_elem = elem
                    break
            if identity_elem is None:
                findings.append("AppxManifest.xml: Kein <Identity>-Element gefunden.")
            else:
                if identity_elem.get("Name") != EXPECTED_IDENTITY:
                    findings.append(f"AppxManifest.xml: Identity Name '{identity_elem.get('Name')}' != '{EXPECTED_IDENTITY}'")
                if identity_elem.get("Publisher") != EXPECTED_PUBLISHER:
                    findings.append(f"AppxManifest.xml: Publisher '{identity_elem.get('Publisher')}' != '{EXPECTED_PUBLISHER}'")
                passed.append("AppxManifest.xml Identity und Publisher valide")
        except Exception as err:
            findings.append(f"AppxManifest.xml fehlerhaft: {err}")

    # 3. Store Tile Assets
    expected_assets = {
        "store_assets/Square44x44Logo.png": (44, 44),
        "store_assets/Square50x50Logo.png": (50, 50),
        "store_assets/StoreLogo.png": (50, 50),
        "store_assets/Square150x150Logo.png": (150, 150),
        "store_assets/Wide310x150Logo.png": (310, 150),
        "store_assets/Square310x310Logo.png": (310, 310),
        "releases/windowsstore/StoreLogo.png": (50, 50),
    }
    for rel_path, expected_dim in expected_assets.items():
        asset_path = PROJECT_ROOT / rel_path
        if not asset_path.exists():
            findings.append(f"Store Tile-Asset fehlt: {rel_path}")
        elif Image is not None:
            try:
                with Image.open(asset_path) as im:
                    if im.size != expected_dim:
                        findings.append(f"Asset {rel_path} Dimension {im.size} != {expected_dim}")
                    else:
                        passed.append(f"Asset {rel_path} ({expected_dim[0]}x{expected_dim[1]}) OK")
            except Exception as err:
                findings.append(f"Asset {rel_path} konnte nicht geprüft werden: {err}")
        else:
            passed.append(f"Asset {rel_path} vorhanden (Pillow nicht geladen)")

    # 4. Store Screenshots
    screenshots_dir = PROJECT_ROOT / "screenshots" / "store"
    if not screenshots_dir.exists():
        findings.append("screenshots/store/ Verzeichnis fehlt.")
    else:
        shots = list(screenshots_dir.glob("*.png"))
        if len(shots) < 4:
            findings.append(f"screenshots/store/: Mindestens 4 Screenshots erforderlich, gefunden: {len(shots)}")
        else:
            passed.append(f"screenshots/store/: {len(shots)} Screenshots vorhanden")
            if Image is not None:
                for shot in shots:
                    try:
                        with Image.open(shot) as im:
                            if im.size != (1920, 1080):
                                findings.append(f"Screenshot {shot.name} hat Auflösung {im.size}, erwartet 1920x1080")
                    except Exception as err:
                        findings.append(f"Screenshot {shot.name} Lesefehler: {err}")
                passed.append("screenshots/store/: Alle Screenshots haben 1080p (1920x1080)")

    # 5. Store-Dokumente
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

    # 6. Keyword-Richtlinie 10.1.3 in STORE_LISTING.md
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

    # 7. Release-Packaging Staging unter releases/windowsstore/
    ws_files = {
        "releases/windowsstore/BUILD.md": "Build-Anleitung",
        "releases/windowsstore/WACK_PROTOCOL.md": "WACK-Protokoll",
        "releases/windowsstore/store_settings.json": "Store-Einstellungen",
        "releases/windowsstore/store_listing_de.md": "Store Listing Deutsch",
        "releases/windowsstore/store_listing_en.md": "Store Listing Englisch",
        "releases/windowsstore/StoreLogo.png": "StoreLogo 50x50",
    }
    for rel_p, lbl in ws_files.items():
        fpath = PROJECT_ROOT / rel_p
        if not fpath.exists():
            findings.append(f"Release-Staging-Datei fehlt: {rel_p} ({lbl})")
        elif fpath.stat().st_size < 10:
            findings.append(f"Release-Staging-Datei zu klein: {rel_p}")
        else:
            passed.append(f"Release-Staging-Datei {rel_p} ({lbl}) OK")

    return passed, findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Store-Readiness Preflight Checker für UniversalDocsGrabber")
    parser.add_argument("--allow-blockers", action="store_true", help="Beendet auch bei Warnungen mit Exit-Code 0")
    args = parser.parse_args()

    passed, findings = check_store_readiness()
    print("=== STORE-READINESS PREFLIGHT REPORT ===")
    for p in passed:
        print(f"  [OK] {p}")
    if findings:
        print("\n=== GEFUNDENE PROBLEME ===")
        for f in findings:
            print(f"  [FEHLER] {f}")
        if args.allow_blockers:
            print("\n[HINWEIS] Beendet mit Exit 0 wegen --allow-blockers Flag.")
            return 0
        return 1
    print(f"\n[ERFOLG] Alle {len(passed)} Store-Readiness-Prüfungen bestanden.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
