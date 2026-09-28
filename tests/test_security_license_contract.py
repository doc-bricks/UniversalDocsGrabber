"""Security, licensing, dependency floor, and privacy contract tests for UniversalDocsGrabber."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_dependency_security_minimum_floors() -> None:
    pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    requirements = (ROOT / "requirements.txt").read_text(encoding="utf-8")
    dev_requirements = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")

    # Minimum secure floors in pyproject.toml
    assert "PySide6>=6.5.0" in pyproject
    assert "pypdf>=4.0.0" in pyproject
    assert "Pillow>=10.4.0" in pyproject
    assert "keyring>=25.0.0" in pyproject
    assert "support@lukasgeiger.com" in pyproject

    # Optional dependencies sections in pyproject.toml
    assert "[project.optional-dependencies]" in pyproject
    assert "pytest>=9.1.1" in pyproject
    assert "ruff>=0.9.0" in pyproject
    assert "pyinstaller>=6.10.0" in pyproject
    assert "altgraph>=0.17.4" in pyproject
    assert "packaging>=24.0" in pyproject

    # Minimum secure floors in requirements.txt
    assert "PySide6>=6.5.0" in requirements
    assert "pypdf>=4.0.0" in requirements
    assert "Pillow>=10.4.0" in requirements
    assert "keyring>=25.0.0" in requirements

    # Minimum secure floors in requirements-dev.txt
    assert "pytest>=9.1.1" in dev_requirements
    assert "ruff>=0.9.0" in dev_requirements
    assert "pyinstaller>=6.10.0" in dev_requirements
    assert "altgraph>=0.17.4" in dev_requirements
    assert "packaging>=24.0" in dev_requirements


def test_third_party_license_inventory_completeness() -> None:
    tp_file = ROOT / "THIRD_PARTY_LICENSES.txt"
    assert tp_file.exists()
    tp_text = tp_file.read_text(encoding="utf-8")

    assert re.search(r"Stand:\s*2026-\d{2}-\d{2}", tp_text), "Must contain valid 2026 audit date"
    assert "Stand: 2026-09-28" in tp_text

    # Standard 5-field schema validation
    assert "Package:" in tp_text
    assert "License:" in tp_text
    assert "SPDX:" in tp_text
    assert "URL:" in tp_text
    assert "Notice:" in tp_text

    required_components = [
        "PySide6",
        "Qt6",
        "PySide6_Addons",
        "PySide6_Essentials",
        "shiboken6",
        "pypdf",
        "reportlab",
        "Pillow",
        "xhtml2pdf",
        "keyring",
        "pytesseract",
        "pdf2image",
        "pywin32",
        "docx2pdf",
        "Tesseract OCR",
        "Poppler",
        "pytest",
        "pluggy",
        "iniconfig",
        "ruff",
        "PyInstaller",
        "altgraph",
        "packaging",
        "setuptools",
    ]
    for comp in required_components:
        assert comp in tp_text, f"Missing third party license declaration for: {comp}"

    # SPDX identifier checks
    assert "SPDX: LGPL-3.0-only" in tp_text
    assert "SPDX: BSD-3-Clause" in tp_text
    assert "SPDX: HPND" in tp_text
    assert "SPDX: Apache-2.0" in tp_text
    assert "SPDX: MIT" in tp_text
    assert "SPDX: PSF-2.0" in tp_text
    assert "SPDX: GPL-2.0-or-later" in tp_text


def test_no_hardcoded_user_paths_in_repo() -> None:
    suspicious = []
    forbidden = "C:" + "\\Users\\"
    forbidden_fwd = "C:" + "/Users/"
    for py_file in ROOT.rglob("*.py"):
        if py_file.name == Path(__file__).name:
            continue
        if any(part in py_file.parts for part in (".venv", "venv", ".build_venv", "build", "dist", "_archive")):
            continue
        text = py_file.read_text(encoding="utf-8", errors="ignore")
        if forbidden in text or forbidden_fwd in text:
            suspicious.append(py_file.name)
    assert not suspicious, f"Hardcoded user paths found in: {suspicious}"


def test_no_plaintext_secrets_or_api_keys() -> None:
    secret_patterns = [
        re.compile(r"(?i)(?:bearer|token|secret|password|api[_-]?key)\s*[:=]\s*['\"][a-zA-Z0-9_\-]{20,}['\"]"),
        re.compile(r"ghp_[a-zA-Z0-9]{36}"),
        re.compile(r"gho_[a-zA-Z0-9]{36}"),
    ]
    violations = []
    for f in LOCAL_files_iter():
        text = f.read_text(encoding="utf-8", errors="ignore")
        for pat in secret_patterns:
            if pat.search(text):
                violations.append(f.name)
    assert not violations, f"Plaintext secrets detected in: {violations}"


def LOCAL_files_iter():
    skip_suffixes = {
        ".png", ".ico", ".jpg", ".jpeg", ".exe", ".pdf", ".traineddata",
        ".zip", ".msix", ".msixupload", ".appx", ".appxupload", ".tar",
        ".gz", ".7z", ".dll", ".so", ".dylib", ".pyd", ".pyc"
    }
    for f in ROOT.rglob("*"):
        if not f.is_file():
            continue
        if any(part in f.parts for part in (".git", ".pytest_cache", ".ruff_cache", "assets", "store_assets", "README", "build", "dist")):
            continue
        if f.suffix.lower() in skip_suffixes:
            continue
        if f.stat().st_size > 2_000_000:
            continue
        yield f


def test_gitignore_security_and_conflict_rules() -> None:
    gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert ".env" in gitignore
    assert "credentials.json" in gitignore
    assert "token.json" in gitignore
    assert "secrets.*" in gitignore
    assert "keyring/" in gitignore
    assert "*.pem" in gitignore
    assert "*.key" in gitignore
    assert "*.pfx" in gitignore
    assert "*.p12" in gitignore
    assert "*.cer" in gitignore
    assert "*.crt" in gitignore
    assert "LOCK*.txt" in gitignore
    assert "*-WORKSTATION-LG*" in gitignore
    assert "*-ASUS-GEI*" in gitignore
    assert "*-conflict-*" in gitignore
    assert "*-CONFLIT-*" in gitignore
    assert "pytest_out.txt" in gitignore
    assert "pytest*.txt" in gitignore
    assert "*.bak" in gitignore


def test_security_policy_bilingual_and_sla() -> None:
    sec_file = ROOT / "SECURITY.md"
    assert sec_file.is_file()
    sec = sec_file.read_text(encoding="utf-8")

    assert "## Deutsch" in sec
    assert "## English" in sec
    assert "security@open-bricks.org" in sec
    assert "security@doc-bricks.org" in sec
    assert "security@ellmos.ai" in sec
    assert "support@lukasgeiger.com" in sec
    assert "https://github.com/doc-bricks/UniversalDocsGrabber/security/advisories/new" in sec
    assert "48 Stunden" in sec or "48 hours" in sec
    assert "5 Werktagen" in sec or "5 business days" in sec
    assert "Zero-Egress" in sec
    assert "RunAsInvoker" in sec or "Non-Elevation" in sec
    assert "Windows Credential Vault" in sec or "keyring" in sec


def test_local_first_and_offline_invariants() -> None:
    disallowed_patterns = [
        re.compile(r"google-analytics\.com", re.IGNORECASE),
        re.compile(r"mixpanel\.com", re.IGNORECASE),
        re.compile(r"segment\.io", re.IGNORECASE),
        re.compile(r"sentry\.io", re.IGNORECASE),
    ]

    py_files = [f for f in ROOT.glob("*.py") if f.is_file()]
    assert len(py_files) >= 2, "Expected at least 2 top-level Python files"

    for py_file in py_files:
        text = py_file.read_text(encoding="utf-8")
        for pat in disallowed_patterns:
            assert not pat.search(text), f"Disallowed telemetry pattern {pat.pattern} found in {py_file.name}"


def test_license_compatibility_and_subprocesses() -> None:
    tp_text = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")
    md_text = (ROOT / "THIRD_PARTY_LICENSES.md").read_text(encoding="utf-8")

    assert "MIT-Lizenz" in tp_text or "MIT License" in tp_text
    assert "dynamische Bindung" in tp_text or "Dynamically linked" in tp_text
    assert "Subprozess-Isolation" in tp_text or "process boundary" in md_text
    assert "Bootloader" in tp_text
    assert "Poppler" in tp_text
    assert "Tesseract" in tp_text
