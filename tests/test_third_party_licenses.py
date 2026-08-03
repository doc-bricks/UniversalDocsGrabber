"""Guard the release license inventory against dependency drift."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def test_third_party_license_inventory_matches_runtime_manifests():
    inventory = (ROOT / "THIRD_PARTY_LICENSES.txt").read_text(encoding="utf-8")
    requirements = [
        line.strip()
        for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    ]
    package_json = json.loads(
        (ROOT / "web_companion" / "package.json").read_text(encoding="utf-8")
    )

    assert "Checked: 2026-08-03" in inventory
    assert "licensed under MIT according to `LICENSE`" in inventory
    assert "not a frozen transitive SBOM" in inventory
    for requirement in requirements:
        assert f"`{requirement}`" in inventory
    for package in ("PySide6_Addons", "PySide6_Essentials", "shiboken6"):
        assert f"| {package} |" in inventory
    assert not package_json.get("dependencies")
    assert not package_json.get("devDependencies")
    assert "`web_companion/package.json` has no dependencies or devDependencies" in inventory
