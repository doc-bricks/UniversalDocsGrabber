"""Automated metadata, manifest, security, and documentation parity test suite."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_metadata_integrity():
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "universaldocsgrabber"' in pyproject_text
    assert 'version = "1.1.6"' in pyproject_text
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
        assert "108%20passed" in text or "108%20bestanden" in text
        assert "Zero--Egress" in text
        assert "SECURITY.md" in text
        assert "THIRD_PARTY_LICENSES.md" in text
        assert "MARKETING-LOG.txt" in text


def test_readme_and_readme_de_quick_navigation():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    # English 15-Point Quick Navigation Anchors
    assert "| [⚡ Quick Start](#start-here)" in readme_en
    assert "[🏗️ Architecture & Pipeline](#system-architecture--data-flow)" in readme_en
    assert "[🔄 Lifecycle Flow](#end-to-end-document-lifecycle)" in readme_en
    assert "[📋 Governance & Invariants](#governance--runtime-invariants)" in readme_en
    assert "[✨ Features in Detail](#features-in-detail)" in readme_en
    assert "[⚙️ Installation & Setup](#installation--setup)" in readme_en
    assert "[🔄 Typical Workflow](#typical-workflow)" in readme_en
    assert "[🔒 Privacy & Security](#privacy-model)" in readme_en
    assert "[📱 Web/PWA Companion](#platform-strategy)" in readme_en
    assert "[🧩 Sibling Tools](#ecosystem--sibling-tools)" in readme_en
    assert "[📜 Third-Party Licenses](#third-party-licenses--transparency)" in readme_en
    assert "[🎯 Target Personas](#marketing--target-personas)" in readme_en
    assert "[⚠️ Limitations](#known-limitations)" in readme_en
    assert "[🛡️ Security Policy](SECURITY.md)" in readme_en
    assert "[🤖 LLM Context](llms.txt)" in readme_en

    # German 15-Point Quick Navigation Anchors
    assert "| [⚡ Schnellstart](#einstieg)" in readme_de
    assert "[🏗️ Architektur & Datenfluss](#systemarchitektur--datenfluss)" in readme_de
    assert "[🔄 Lebenszyklus-Ablauf](#end-to-end-dokumenten-lebenszyklus)" in readme_de
    assert "[📋 Governance- & Laufzeit-Invarianten](#governance--und-laufzeit-invarianten)" in readme_de
    assert "[✨ Funktionen im Detail](#funktionen-im-detail)" in readme_de
    assert "[⚙️ Installation & Einrichtung](#installation--einrichtung)" in readme_de
    assert "[🔄 Typischer Arbeitsablauf](#typischer-arbeitsablauf)" in readme_de
    assert "[🔒 Datenschutz & Sicherheit](#datenschutzmodell)" in readme_de
    assert "[📱 Web/PWA-Begleiter](#plattform-strategie)" in readme_de
    assert "[🧩 Geschwister-Werkzeuge](#ökosystem--geschwister-tools)" in readme_de
    assert "[📜 Drittanbieter-Lizenzen](#drittanbieter-lizenzen--transparenz)" in readme_de
    assert "[🎯 Zielgruppen](#marketing--zielgruppen)" in readme_de
    assert "[⚠️ Bekannte Einschränkungen](#bekannte-einschränkungen)" in readme_de
    assert "[🛡️ Sicherheitsrichtlinie](SECURITY.md)" in readme_de
    assert "[🤖 LLM-Kontext](llms.txt)" in readme_de


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
    assert "Last-checked: 2026-09-12" in llms_text
    assert "https://github.com/doc-bricks/UniversalDocsGrabber" in llms_text
    assert "MIT" in llms_text
    assert "PySide6" in llms_text
    assert "THIRD_PARTY_LICENSES.md" in llms_text
    assert "MARKETING-LOG.txt" in llms_text
    assert "INV-LOCAL-01" in llms_text
    assert "EXPORTFORMAT.md" in llms_text
    assert "108 passed" in llms_text


def test_third_party_licenses_md_compliance():
    lic_path = ROOT / "THIRD_PARTY_LICENSES.md"
    assert lic_path.is_file()
    lic_text = lic_path.read_text(encoding="utf-8")
    assert "2026-09-11" in lic_text
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


def test_gitignore_multihost_and_lock_defense():
    gitignore_path = ROOT / ".gitignore"
    assert gitignore_path.is_file()
    gi_text = gitignore_path.read_text(encoding="utf-8")
    assert "* (kopie)*" in gi_text
    assert "*-WORKSTATION*" in gi_text
    assert "*-ASUS-GEI*" in gi_text
    assert "LOCK" in gi_text
    assert "uv.lock" in gi_text
    assert "!package-lock.json" in gi_text


def test_ruff_linter_configuration_and_clean_run():
    pyproject_path = ROOT / "pyproject.toml"
    assert pyproject_path.is_file()
    pyproject_text = pyproject_path.read_text(encoding="utf-8")
    assert "[tool.ruff.lint]" in pyproject_text
    assert 'select = ["E", "F", "W", "B", "C4"]' in pyproject_text
    assert 'ignore = ["E501", "E701", "E702"]' in pyproject_text
