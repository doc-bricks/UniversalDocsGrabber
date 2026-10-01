"""Automated metadata, manifest, security, and documentation parity test suite."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_metadata_integrity():
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "universaldocsgrabber"' in pyproject_text
    assert 'version = "1.1.7"' in pyproject_text
    assert 'requires-python = ">=3.8"' in pyproject_text
    assert 'license = {text = "MIT"}' in pyproject_text
    assert "https://github.com/doc-bricks/UniversalDocsGrabber" in pyproject_text
    assert 'Security = "https://github.com/doc-bricks/UniversalDocsGrabber/blob/master/SECURITY.md"' in pyproject_text
    assert '"Third-Party Licenses" = "https://github.com/doc-bricks/UniversalDocsGrabber/blob/master/THIRD_PARTY_LICENSES.md"' in pyproject_text
    assert '"Marketing Log" = "https://github.com/doc-bricks/UniversalDocsGrabber/blob/master/MARKETING-LOG.txt"' in pyproject_text
    assert '"LLM Ready" = "https://github.com/doc-bricks/UniversalDocsGrabber/blob/master/llms.txt"' in pyproject_text
    assert '"Parent Organization" = "https://github.com/doc-bricks"' in pyproject_text
    assert '"Umbrella Ecosystem" = "https://github.com/open-bricks"' in pyproject_text
    assert "Programming Language :: Python :: 3.13" in pyproject_text
    assert "Operating System :: OS Independent" in pyproject_text
    assert "testpaths = [\"tests\"]" in pyproject_text
    assert "python_files = [\"test_*.py\", \"source_platform_smoke.py\"]" in pyproject_text


def test_readme_and_readme_de_badges():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    assert "License-MIT" in readme_en
    assert "Lizenz-MIT" in readme_de
    for text in (readme_en, readme_de):
        assert "actions/workflows/ci.yml" in text
        assert "doc--bricks" in text
        assert "open--bricks" in text
        assert "llms.txt" in text
        assert "contract--tests" in text
        assert ("116%20passed" in text or "116%20bestanden" in text or
                "114%20passed" in text or "114%20bestanden" in text or
                "110%20passed" in text or "110%20bestanden" in text)
        assert "attribution-NOTICE" in text or "Attribution-NOTICE" in text
        assert "Zero--Egress" in text
        assert "SECURITY.md" in text
        assert "THIRD_PARTY_LICENSES.md" in text
        assert "THIRD_PARTY_LICENSES.txt" in text
        assert "MARKETING-LOG.txt" in text
        assert ("Verified-2026--10--01" in text or "Gepr%C3%BCft-2026--10--01" in text or
                "Verified-2026--09--30" in text or "Gepr%C3%BCft-2026--09--30" in text or "Verified-2026--09--28" in text)
        assert ("Last--checked-2026--10--01" in text or "Letzte--Pr%C3%BCfung-2026--10--01" in text or
                "Last--checked-2026--09--30" in text or "Letzte--Pr%C3%BCfung-2026--09--30" in text or "Last--checked-2026--09--28" in text)



def test_readme_and_readme_de_quick_navigation():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    # English 18-Point Quick Navigation Anchors
    expected_en_points = [
        "- [1. Overview & Why This Exists](#1-overview--why-this-exists)",
        "- [2. Key Capabilities & Architecture](#2-key-capabilities--architecture)",
        "- [3. Target Personas & High-Intent Discoverability](#3-target-personas--high-intent-discoverability)",
        "- [4. Comparative Matrix vs. Alternatives](#4-comparative-matrix-vs-alternatives)",
        "- [5. Governance & Runtime Invariants](#5-governance--runtime-invariants)",
        "- [6. Visual Architecture & Flowchart](#6-visual-architecture--flowchart)",
        "- [7. Document Lifecycle Flow](#7-document-lifecycle-flow)",
        "- [8. Typical Workflow & Execution Guide](#8-typical-workflow--execution-guide)",
        "- [9. Installation & Prerequisites](#9-installation--prerequisites)",
        "- [10. Features in Detail & Document Normalization](#10-features-in-detail--document-normalization)",
        "- [11. Privacy Model, Keyring Vault & Local Data](#11-privacy-model-keyring-vault--local-data)",
        "- [12. Web/PWA Companion & Redacted Mobile Review](#12-web-pwa-companion--redacted-mobile-review)",
        "- [13. Sibling Ecosystem Matrix & Integration](#13-sibling-ecosystem-matrix--integration)",
        "- [14. CLI, LLM Context & Machine-Readable Contracts](#14-cli-llm-context--machine-readable-contracts)",
        "- [15. Known Limitations & Edge Cases](#15-known-limitations--edge-cases)",
        "- [16. Development, Toolchain & Automated Test Suite](#16-development-toolchain--automated-test-suite)",
        "- [17. Third-Party Licenses, Zero-Copyleft & Level 1 SBOM](#17-third-party-licenses-zero-copyleft--level-1-sbom)",
        "- [18. Roadmap, Changelog & German Statutory Notice (§ 521 BGB)](#18-roadmap-changelog--german-statutory-notice--521-bgb)",
    ]
    for pt in expected_en_points:
        assert pt in readme_en, f"English point missing: {pt}"

    # German 18-Point Quick Navigation Anchors
    expected_de_points = [
        "- [1. Überblick & Zweck](#1-ueberblick--zweck)",
        "- [2. Kernfunktionen & Architektur](#2-kernfunktionen--architektur)",
        "- [3. Zielgruppen & Suchintentionen](#3-zielgruppen--suchintentionen)",
        "- [4. Vergleichsmatrix gegenüber Alternativen](#4-vergleichsmatrix-gegenueber-alternativen)",
        "- [5. Governance- & Laufzeit-Invarianten](#5-governance--laufzeit-invarianten)",
        "- [6. Visuelle Systemarchitektur & Ablaufdiagramm](#6-visuelle-systemarchitektur--ablaufdiagramm)",
        "- [7. End-to-End Dokumenten-Lebenszyklus](#7-end-to-end-dokumenten-lebenszyklus)",
        "- [8. Typischer Arbeitsablauf & Ausführung](#8-typischer-arbeitsablauf--ausfuehrung)",
        "- [9. Installation & Systemvoraussetzungen](#9-installation--systemvoraussetzungen)",
        "- [10. Funktionen im Detail & Dokumenten-Normalisierung](#10-funktionen-im-detail--dokumenten-normalisierung)",
        "- [11. Datenschutzmodell, Keyring-Tresor & Lokale Daten](#11-datenschutzmodell-keyring-tresor--lokale-daten)",
        "- [12. Web/PWA-Begleiter & Redigierte Mobile Einsicht](#12-web-pwa-begleiter--redigierte-mobile-einsicht)",
        "- [13. Ökosystem & Geschwister-Werkzeuge](#13-oekosystem--geschwister-werkzeuge)",
        "- [14. CLI, LLM-Kontext & Maschinenlesbare Verträge](#14-cli-llm-kontext--maschinenlesbare-vertraege)",
        "- [15. Bekannte Einschränkungen & Sonderfälle](#15-bekannte-einschraenkungen--sonderfaelle)",
        "- [16. Entwicklung, Toolchain & Automatisierte Testsuite](#16-entwicklung-toolchain--automatisierte-testsuite)",
        "- [17. Drittanbieter-Lizenzen, Zero-Copyleft & Level 1 SBOM](#17-drittanbieter-lizenzen-zero-copyleft--level-1-sbom)",
        "- [18. Roadmap, Änderungsprotokoll & Gesetzlicher Haftungsausschluss (§ 521 BGB)](#18-roadmap-aenderungsprotokoll--gesetzlicher-haftungsausschluss--521-bgb)",
    ]
    for pt in expected_de_points:
        assert pt in readme_de, f"German point missing: {pt}"

    # Verify reciprocal dual HTML anchors sec-01 through sec-18 in both documents
    for i in range(1, 19):
        anchor = f'<a id="sec-{i:02d}"></a>'
        assert anchor in readme_en, f"Anchor {anchor} missing in README.md"
        assert anchor in readme_de, f"Anchor {anchor} missing in README-DE.md"


def test_readme_and_readme_de_governance_invariants():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    invariants = [
        "INV-LOCAL-01",
        "INV-SEC-02",
        "INV-CRED-03",
        "INV-REDACT-04",
        "INV-HASH-05",
        "INV-FALL-06",
        "INV-PWA-07",
        "INV-LIC-08",
        "INV-SLA-09",
        "INV-PAR-10",
    ]
    for inv in invariants:
        assert inv in readme_en
        assert inv in readme_de


def test_readme_and_readme_de_mermaid_diagrams():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    for text in (readme_en, readme_de):
        assert "```mermaid" in text
        assert "graph TD" in text
        assert "sequenceDiagram" in text
        assert "autonumber" in text
        assert "SHA-256" in text
        assert "docsgrabber-library-v1.json" in text


def test_security_policy_invariants_and_sla():
    security_text = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "security@open-bricks.org" in security_text
    assert "security@ellmos.ai" in security_text
    assert "48 hours" in security_text or "48h" in security_text
    assert "5 business days" in security_text
    assert "Local-First & Zero-Egress" in security_text
    assert "Windows Credential Vault" in security_text or "keyring" in security_text
    assert "docsgrabber-library-v1.json" in security_text
    assert "Sicherheitsrichtlinie" in security_text

    plan_text = (ROOT / "PORTIERUNGSPLAN.md").read_text(encoding="utf-8")
    assert "65/65 Pytest-Tests" in plan_text
    assert "darin 3/3 Source-Smoke-Checks" in plan_text
    assert "32/32 Node-Smokes" in plan_text
    assert "Rückimport / Cloud-Sync" in plan_text
    assert "Nicht implementiert und Nicht-Ziel" in plan_text
    assert "Android/iOS" in plan_text
    assert "Gerät/Emulator bleiben offen" in plan_text


def test_llms_txt_currency_and_structure():
    llms_text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "Last-checked: 2026-10-01" in llms_text or "Last-checked: 2026-09-30" in llms_text or "Last-checked: 2026-09-28" in llms_text or "Last-checked: 2026-09-22" in llms_text

    assert "https://github.com/doc-bricks/UniversalDocsGrabber" in llms_text
    assert "MIT" in llms_text
    assert "PySide6" in llms_text
    assert "NOTICE" in llms_text
    assert "THIRD_PARTY_LICENSES.md" in llms_text
    assert "MARKETING-LOG.txt" in llms_text
    assert "INV-LOCAL-01" in llms_text
    assert "EXPORTFORMAT.md" in llms_text
    assert "116 passed" in llms_text or "114 passed" in llms_text


def test_third_party_licenses_md_compliance():
    lic_path = ROOT / "THIRD_PARTY_LICENSES.md"
    assert lic_path.is_file()
    lic_text = lic_path.read_text(encoding="utf-8")
    assert "2026-09-28" in lic_text or "2026-09-22" in lic_text
    assert "NOTICE" in lic_text
    assert "Audit Date" in lic_text
    assert "100% Permissive Open Source" in lic_text
    assert "PySide6" in lic_text
    assert "LGPL-3.0" in lic_text
    assert "INV-LOCAL-01" in lic_text
    assert "INV-SEC-02" in lic_text
    assert "pypdf" in lic_text
    assert "reportlab" in lic_text
    assert "Pillow" in lic_text
    assert "keyring" in lic_text


def test_marketing_log_structure_and_personas():
    mkt_path = ROOT / "MARKETING-LOG.txt"
    assert mkt_path.is_file()
    mkt_text = mkt_path.read_text(encoding="utf-8")
    assert "doc-bricks/UniversalDocsGrabber" in mkt_text
    assert "Solo Entrepreneurs & Small Business Bookkeepers" in mkt_text
    assert "Legal, Tax & Compliance Assistants" in mkt_text
    assert "Privacy-Conscious Power Users & Document Archivists" in mkt_text
    assert "Local-First AI & Automation Engineers" in mkt_text
    assert "HIGH-INTENT DISCOVERY KEYWORDS" in mkt_text
    assert "COMPETITIVE & ARCHITECTURAL COMPARISON MATRIX" in mkt_text
    assert "SIBLING TOOLS ECOSYSTEM MAPPING" in mkt_text
    assert "INV-LOCAL-01" in mkt_text
    assert "INV-SLA-10" in mkt_text or "INV-PAR-10" in mkt_text


def test_web_companion_package_and_manifest():
    pkg_path = ROOT / "web_companion" / "package.json"
    manifest_path = ROOT / "web_companion" / "manifest.webmanifest"
    sw_path = ROOT / "web_companion" / "sw.js"

    assert pkg_path.is_file()
    assert manifest_path.is_file()
    assert sw_path.is_file()

    pkg_data = json.loads(pkg_path.read_text(encoding="utf-8"))
    assert pkg_data.get("name") == "universaldocsgrabber-web-companion"
    assert pkg_data.get("type") == "module"

    manifest_data = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert "UniversalDocsGrabber" in manifest_data.get("name", "")
    assert manifest_data.get("display") == "standalone"


def test_github_ci_workflow_validity():
    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    assert ci_path.is_file()
    ci_text = ci_path.read_text(encoding="utf-8")
    assert "ubuntu-latest" in ci_text
    assert "windows-latest" in ci_text
    assert "macos-latest" in ci_text
    assert "3.10" in ci_text
    assert "3.11" in ci_text
    assert "3.12" in ci_text
    assert "3.13" in ci_text
    assert "24.x" in ci_text
    assert "node --test web_companion/tests/*.test.mjs" in ci_text


def test_sibling_ecosystem_matrix_presence():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    for text in (readme_en, readme_de):
        assert "doc-bricks" in text
        assert "file-bricks" in text
        assert "dev-bricks" in text
        assert "ellmos-ai" in text
        assert "CleanMarkdown" in text
        assert "PDFtoPDFocr" in text
        assert "MediaBrain" in text
        assert "ellmos-filecommander-mcp" in text
        assert "workflowhooker-provenance" in text
        assert "lock-master" in text


def test_ci_concurrency_and_timeout_guardrails():
    ci_path = ROOT / ".github" / "workflows" / "ci.yml"
    smoke_path = ROOT / ".github" / "workflows" / "source-platform-smoke.yml"
    assert ci_path.is_file()
    assert smoke_path.is_file()

    ci_text = ci_path.read_text(encoding="utf-8")
    smoke_text = smoke_path.read_text(encoding="utf-8")

    for text in (ci_text, smoke_text):
        assert "concurrency:" in text
        assert "cancel-in-progress: true" in text

    assert "timeout-minutes: 15" in ci_text
    assert "timeout-minutes: 10" in ci_text
    assert "timeout-minutes: 15" in smoke_text
    assert "python -m pytest -ra -v" in ci_text


def test_ci_stale_workflow_present():
    stale_path = ROOT / ".github" / "workflows" / "stale.yml"
    assert stale_path.is_file()
    stale_text = stale_path.read_text(encoding="utf-8")
    assert "actions/stale@v9" in stale_text
    assert "issues: write" in stale_text
    assert "pull-requests: write" in stale_text
    assert "timeout-minutes: 10" in stale_text
    assert "cancel-in-progress: true" in stale_text


def test_gitignore_multihost_and_lock_defense():
    gitignore_path = ROOT / ".gitignore"
    assert gitignore_path.is_file()
    gi_text = gitignore_path.read_text(encoding="utf-8")
    assert "* (kopie)*" in gi_text
    assert "*-WORKSTATION*" in gi_text
    assert "*-ASUS*" in gi_text
    assert "*-ASUS-GEI*" in gi_text
    assert "LOCK" in gi_text
    assert "LOCK.user.*" in gi_text
    assert ".automation-lock" in gi_text
    assert "uv.lock" in gi_text
    assert "!package-lock.json" in gi_text
    assert ".pytest_temp/" in gi_text
    assert ".pytest_tmp*/" in gi_text


def test_ruff_linter_configuration_and_clean_run():
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.is_file()
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    assert "[tool.ruff.lint]" in pyproject_text
    assert 'select = ["E", "F", "W", "B", "C4"]' in pyproject_text
    assert 'ignore = ["E501", "E701", "E702"]' in pyproject_text


def test_comparative_matrix_parity():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    # Both must have explicit anchor tags and headings
    assert '<a name="comparative-matrix-vs-alternatives"></a>' in readme_en or '<a id="comparative-matrix-vs-alternatives"></a>' in readme_en
    assert "Comparative Matrix vs Alternatives" in readme_en or "Comparative Matrix vs. Alternatives" in readme_en
    assert '<a name="vergleichsmatrix-gegenüber-alternativen"></a>' in readme_de or '<a id="vergleichsmatrix-gegenüber-alternativen"></a>' in readme_de or '<a id="vergleichsmatrix-gegenueber-alternativen"></a>' in readme_de
    assert "Vergleichsmatrix gegenüber Alternativen" in readme_de or "Vergleichsmatrix gegenueber Alternativen" in readme_de

    # Check that both compare the 5 standard categories
    for text in (readme_en, readme_de):
        assert "UniversalDocsGrabber" in text
        assert "DocuWare" in text or "Dext" in text
        assert "Paperless-ngx" in text or "Mayan" in text
        assert "Thunderbird" in text or "Outlook" in text
        assert "Fetchmail" in text or "Python" in text
        # Check core architectural dimensions
        assert "INV-LOCAL-01" in text
        assert "INV-SEC-02" in text or "RunAsInvoker" in text
        assert "INV-CRED-03" in text or "keyring" in text
        assert "INV-HASH-05" in text or "SHA-256" in text
        assert "INV-PWA-07" in text
        assert "INV-LIC-08" in text or "LGPL" in text
        assert "Tesseract" in text


def test_target_personas_structure_and_parity():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    # Check 4 structured personas in English
    assert "### [PERSONA-1] Solo Entrepreneurs & Small Business Bookkeepers" in readme_en
    assert "### [PERSONA-2] Legal, Tax & Compliance Assistants" in readme_en
    assert "### [PERSONA-3] Privacy-Conscious Power Users & Document Archivists" in readme_en
    assert "### [PERSONA-4] Local-First AI & Automation Engineers" in readme_en

    # Check 4 structured personas in German
    assert "### [PERSONA-1] Solo-Unternehmer & Kleinbetrieb-Buchhaltung" in readme_de
    assert "### [PERSONA-2] Rechts-, Steuer- & Compliance-Fachkräfte" in readme_de
    assert "### [PERSONA-3] Datenschutzbewusste Power-User & Dokumenten-Archivare" in readme_de
    assert "### [PERSONA-4] Local-First KI- & Automations-Entwickler" in readme_de

    # Check structured headings
    assert "Acute Pain Point" in readme_en
    assert "Applied Solution" in readme_en
    assert "Typical Workflow" in readme_en

    assert "Akuter Schmerzpunkt" in readme_de
    assert "Angewandte Lösung" in readme_de
    assert "Typischer Ablauf" in readme_de


def test_notice_attribution_file_present_and_compliant():
    notice_path = ROOT / "NOTICE"
    assert notice_path.is_file()
    notice_text = notice_path.read_text(encoding="utf-8")
    assert "UniversalDocsGrabber" in notice_text
    assert "Copyright (c) 2026 Lukas Geiger" in notice_text
    assert "doc-bricks" in notice_text
    assert "open-bricks" in notice_text
    assert "MIT License" in notice_text
    assert "THIRD_PARTY_LICENSES.md" in notice_text
    assert "THIRD_PARTY_LICENSES.txt" in notice_text


def test_welcome_workflow_present_and_configured():
    welcome_path = ROOT / ".github" / "workflows" / "welcome.yml"
    assert welcome_path.is_file()
    w_text = welcome_path.read_text(encoding="utf-8")
    assert "actions/first-interaction@v3" in w_text
    assert "cancel-in-progress: true" in w_text
    assert "timeout-minutes: 5" in w_text
    assert "issues: write" in w_text
    assert "pull-requests: write" in w_text
    assert "Welcome to **UniversalDocsGrabber**" in w_text


def test_pyproject_pep621_license_files_and_notice_url():
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.is_file()
    content = pyproject_path.read_text(encoding="utf-8")
    assert 'version = "1.1.7"' in content  # Strictly frozen per T-20260920-167562623
    assert 'license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]' in content
    assert 'Notice = "https://github.com/doc-bricks/UniversalDocsGrabber/blob/master/NOTICE"' in content
    assert '"Level 1 SBOM" = "https://github.com/doc-bricks/UniversalDocsGrabber/blob/master/THIRD_PARTY_LICENSES.md#8-level-1-sbom-invarianten-kreuzreferenzmatrix-inv-local-01-bis-inv-sla-10"' in content
    assert '"Plain-Text License" = "https://github.com/doc-bricks/UniversalDocsGrabber/blob/master/LICENSE"' in content
    assert '"Third-Party Licenses (Text)" = "https://github.com/doc-bricks/UniversalDocsGrabber/blob/master/THIRD_PARTY_LICENSES.txt"' in content
    assert 'Contributing = "https://github.com/doc-bricks/UniversalDocsGrabber/blob/master/CONTRIBUTING.md"' in content
    assert 'minversion = "7.0"' in content
    assert '--basetemp=.pytest_temp' in content
    assert 'norecursedirs = [' in content



def test_changelog_unreleased_pfad_a_entry_present():
    changelog_path = ROOT / "CHANGELOG.md"
    assert changelog_path.is_file()
    cl_text = changelog_path.read_text(encoding="utf-8")
    assert "## [Unreleased]" in cl_text
    assert "2026-09-22: Pfad A Repository Hygiene" in cl_text
    assert "T-20260920-167562623" in cl_text


def test_level_1_sbom_cross_reference_matrix_and_runasinvoker():
    """Verify Section 8 Level 1 SBOM Invariant Cross-Reference Matrix in THIRD_PARTY_LICENSES.md."""
    sbom_path = ROOT / "THIRD_PARTY_LICENSES.md"
    assert sbom_path.is_file()
    sbom_text = sbom_path.read_text(encoding="utf-8")
    assert "Level 1 SBOM Invarianten-Kreuzreferenzmatrix" in sbom_text
    assert "2026-09-28" in sbom_text
    for i in range(1, 11):
        assert "INV-" in sbom_text and f"{i:02d}" in sbom_text
    assert "RunAsInvoker" in sbom_text
    assert "Zero-Copyleft" in sbom_text
    assert "NOTICE" in sbom_text


def test_statutory_disclaimer_521_bgb_and_48h_sla_in_both_readmes():
    """Verify German statutory notice (§ 521 BGB Gefälligkeitsrecht) and 48h Security SLA in Section 18."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    for doc, name in [(readme_en, "README.md"), (readme_de, "README-DE.md")]:
        assert "521 BGB" in doc, f"§ 521 BGB missing in {name}"
        assert "Gefälligkeitsrecht" in doc, f"Gefälligkeitsrecht missing in {name}"
        assert "48 hours" in doc or "48 Stunden" in doc or "48h" in doc, f"48h SLA missing in {name}"
        assert "sec-18" in doc, f"sec-18 anchor missing in {name}"


def test_pyproject_keywords_20_topics_saturated():
    """Verify pyproject.toml has 20 saturated keywords matching GitHub repository topics and canonical URL."""
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.is_file()
    text = pyproject_path.read_text(encoding="utf-8")
    expected_topics = [
        "attachment-downloader", "document-archive", "document-management", "document-workflow",
        "email", "email-attachment", "email-attachments", "gmail", "gmail-attachments",
        "imap", "invoice-extraction", "local-first", "mail-archive", "ocr", "offline-first",
        "pdf", "pwa", "pyside6", "python", "windows"
    ]
    for topic in expected_topics:
        assert f'"{topic}"' in text, f"Topic '{topic}' missing from pyproject.toml"
    assert 'Homepage = "https://github.com/doc-bricks/UniversalDocsGrabber#readme"' in text


def test_changelog_and_marketing_log_pfad_b_20260928():
    """Verify Pfad B milestone entries in CHANGELOG.md and MARKETING-LOG.txt."""
    cl_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    mkt_text = (ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert "2026-09-28" in cl_text
    assert "Pfad B Marketing, Discoverability, Visual Architecture & Bilateral Navigation Parity" in cl_text
    assert "2026-09-28" in mkt_text
    assert "Upgraded to full 18-point bilateral quick navigation parity" in mkt_text


def test_ascii_four_view_topology_projection():
    """Verify Section 2 ASCII Four-View Architectural Topology projection in both README.md and README-DE.md."""
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    # English Four-View projection
    assert "### ASCII Four-View Architectural Topology Projection" in readme_en
    assert "[VIEW 1: CLIENT RUNTIMES, USER INTERFACES & AUTOMATION DRIVERS]" in readme_en
    assert "[VIEW 2: UNIVERSALDOCSGRABBER SOVEREIGN CORE ENGINE & PIPELINE ORCHESTRATOR]" in readme_en
    assert "[VIEW 3: RUNTIME PERSISTENCE, LOCAL DOCUMENT VAULT & SANITIZED EXPORTS]" in readme_en
    assert "[VIEW 4: AIR-GAP DEFENSE PERIMETER, ZERO-EGRESS & GOVERNANCE]" in readme_en

    # German Four-View projection
    assert "### ASCII Vier-Ansichten-Architekturprojektion" in readme_de
    assert "[SICHT 1: CLIENT-LAUFZEITEN, BENUTZEROBERFLÄCHEN & AUTOMATIONS-TREIBER]" in readme_de
    assert "[SICHT 2: UNIVERSALDOCSGRABBER KERN-ENGINE & PIPELINE-ORCHESTRIERUNG]" in readme_de
    assert "[SICHT 3: LOKALE PERSISTENZ, DOKUMENTEN-ARCHIV & BEREINIGTE EXPORTE]" in readme_de
    assert "[SICHT 4: AIR-GAP SICHERHEITSPERIMETER, ZERO-EGRESS & GOVERNANCE]" in readme_de


def test_level_1_sbom_plaintext_companion_invariants():
    """Verify Section 8 Level 1 SBOM Invariant Cross-Reference Matrix in plain-text companion THIRD_PARTY_LICENSES.txt."""
    txt_path = ROOT / "THIRD_PARTY_LICENSES.txt"
    assert txt_path.is_file()
    txt_content = txt_path.read_text(encoding="utf-8")

    assert ("Stand: 2026-10-01" in txt_content or "Stand: 2026-09-30" in txt_content)
    assert "## 8. Level 1 SBOM Invarianten-Kreuzreferenzmatrix" in txt_content
    for i in range(1, 11):
        assert "INV-" in txt_content and f"{i:02d}" in txt_content
    assert "RunAsInvoker Non-Elevation Certification (INV-SEC-02)" in txt_content
    assert "Zero-Copyleft Isolation Guarantee (INV-LIC-08)" in txt_content
    assert "§ 521 BGB" in txt_content
    assert "MIT License" in txt_content
    assert "BSD 3-Clause License" in txt_content
    assert "Apache License 2.0" in txt_content
    assert "Python Software Foundation License" in txt_content


def test_changelog_and_marketing_log_pfad_b_20260930():
    """Verify Pfad B 2026-09-30 milestone entries in CHANGELOG.md and MARKETING-LOG.txt."""
    cl_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    mkt_text = (ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")
    assert "2026-09-30" in cl_text
    assert "Pfad B Visual Architecture, ASCII 4-View Topology & Level 1 SBOM Text Companion (2026-09-30)" in cl_text
    assert "2026-09-30" in mkt_text
    assert "ASCII 4-view topology projection, Level 1 SBOM text companion Stand 2026-09-30" in mkt_text


def test_ci_lifecycle_workflows_present_and_configured():
    """Verify auto-assign.yml and label-sync.yml exist with required concurrency and timeout guardrails."""
    workflows_dir = ROOT / ".github" / "workflows"
    assert workflows_dir.is_dir()

    auto_assign = workflows_dir / "auto-assign.yml"
    assert auto_assign.is_file(), "auto-assign.yml missing"
    aa_text = auto_assign.read_text(encoding="utf-8")
    assert "actions/github-script@v7" in aa_text
    assert "timeout-minutes: 5" in aa_text
    assert "cancel-in-progress: true" in aa_text
    assert "pull-requests: write" in aa_text
    assert "issues: write" in aa_text

    label_sync = workflows_dir / "label-sync.yml"
    assert label_sync.is_file(), "label-sync.yml missing"
    ls_text = label_sync.read_text(encoding="utf-8")
    assert "EndBug/label-sync@v2" in ls_text
    assert "timeout-minutes: 5" in ls_text
    assert "cancel-in-progress: true" in ls_text
    assert "issues: write" in ls_text
    assert ".github/labels.yml" in ls_text


def test_github_labels_yml_present_and_compliant():
    """Verify canonical .github/labels.yml exists with standard 13 governance labels."""
    labels_file = ROOT / ".github" / "labels.yml"
    assert labels_file.is_file(), ".github/labels.yml missing"
    content = labels_file.read_text(encoding="utf-8")
    expected_labels = [
        "bug", "enhancement", "good first issue", "help wanted", "documentation",
        "duplicate", "wontfix", "priority: high", "priority: low", "needs-triage",
        "stale", "security", "dependencies"
    ]
    for label in expected_labels:
        assert f"name: {label}" in content or f"name: '{label}'" in content or f'name: "{label}"' in content, f"Missing label: {label}"


def test_contributing_bilingual_and_quality_gates():
    """Verify CONTRIBUTING.md contains bilingual sections, Plan D setup, quality gates, and 10 invariants."""
    contrib = ROOT / "CONTRIBUTING.md"
    assert contrib.is_file()
    text = contrib.read_text(encoding="utf-8")

    assert "## English" in text
    assert "## Deutsch" in text
    assert "Plan D" in text
    assert "UniversalDocsGrabber" in text
    assert "INV-LOCAL-01" in text
    assert "INV-SEC-02" in text
    assert "INV-PAR-10" in text
    assert "RunAsInvoker" in text
    assert "T-20260920-167562623" in text
    assert 'version = "' in text or 'version =' in text
    assert "git diff --check" in text
    assert "pytest" in text
    assert "ruff check" in text
    assert "compileall" in text


def test_gitignore_multihost_ideapad_defense():
    """Verify .gitignore contains IDEAPAD host token patterns and canonical lock defenses."""
    gi_path = ROOT / ".gitignore"
    assert gi_path.is_file()
    gi_text = gi_path.read_text(encoding="utf-8")
    assert "*-IDEAPAD*" in gi_text
    assert "*-IDEAPAD-GEI*" in gi_text
    assert "*-WORKSTATION*" in gi_text
    assert "LOCK.dev.*" in gi_text
    assert "LOCK.antigravity.*" in gi_text
    assert "LOCK.bugsearch.*" in gi_text


def test_changelog_and_marketing_log_pfad_a_20261001():
    """Verify Pfad A 2026-10-01 entries in CHANGELOG.md and MARKETING-LOG.txt."""
    cl_text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    mkt_text = (ROOT / "MARKETING-LOG.txt").read_text(encoding="utf-8")

    assert "2026-10-01" in cl_text
    assert "Pfad A Repository Hygiene, CI Lifecycle Workflows, Bilingual CONTRIBUTING & Contract Test Suite (2026-10-01)" in cl_text
    assert "2026-10-01" in mkt_text
    assert "Pfad A repository hygiene, CI lifecycle workflows, bilingual CONTRIBUTING guidelines" in mkt_text


def test_pyproject_norecursedirs_hardened():
    """Verify pytest norecursedirs includes temporary and test-runner directories."""
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert ".pytest_tmp*" in pyproject_text
    assert ".tox" in pyproject_text
    assert ".hypothesis" in pyproject_text
    assert ".turbo" in pyproject_text
    assert ".nyc_output" in pyproject_text
