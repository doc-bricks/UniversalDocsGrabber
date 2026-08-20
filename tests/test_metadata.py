"""Automated metadata, manifest, security, and documentation parity test suite."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def test_pyproject_metadata_integrity():
    pyproject_text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'name = "universaldocsgrabber"' in pyproject_text
    assert 'version = "1.1.4"' in pyproject_text
    assert 'requires-python = ">=3.8"' in pyproject_text
    assert 'license = {text = "MIT"}' in pyproject_text
    assert "https://github.com/doc-bricks/UniversalDocsGrabber" in pyproject_text
    assert "testpaths = [\"tests\"]" in pyproject_text
    assert "python_files = [\"test_*.py\", \"source_platform_smoke.py\"]" in pyproject_text


def test_readme_and_readme_de_badges():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    assert "License-MIT" in readme_en
    assert "Lizenz-MIT" in readme_de
    for text in (readme_en, readme_de):
        assert "doc--bricks" in text
        assert "open--bricks" in text
        assert "llms.txt" in text
        assert "contract--tests" in text
        assert "95%20passed" in text or "95%20bestanden" in text


def test_security_policy_invariants():
    security_text = (ROOT / "SECURITY.md").read_text(encoding="utf-8")
    assert "security@ellmos.ai" in security_text
    assert "Local-First & Zero-Egress" in security_text
    assert "Windows Credential Vault" in security_text or "keyring" in security_text
    assert "docsgrabber-library-v1.json" in security_text
    assert "Sicherheitsrichtlinie" in security_text


def test_llms_txt_currency_and_structure():
    llms_text = (ROOT / "llms.txt").read_text(encoding="utf-8")
    assert "Last-checked: 2026-08-20" in llms_text
    assert "https://github.com/doc-bricks/UniversalDocsGrabber" in llms_text
    assert "MIT" in llms_text
    assert "PySide6" in llms_text
    assert "EXPORTFORMAT.md" in llms_text


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
    assert "node --test web_companion/tests/*.test.mjs" in ci_text


def test_sibling_ecosystem_matrix_presence():
    readme_en = (ROOT / "README.md").read_text(encoding="utf-8")
    readme_de = (ROOT / "README-DE.md").read_text(encoding="utf-8")

    for text in (readme_en, readme_de):
        assert "doc-bricks" in text
        assert "file-bricks" in text
        assert "CleanMarkdown" in text
        assert "PDFtoPDFocr" in text
        assert "MediaBrain" in text
