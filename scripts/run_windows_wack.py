"""Führt das Windows App Certification Kit (WACK) für UniversalDocsGrabber aus oder wertet vorhandene Reports aus."""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Sequence
import xml.etree.ElementTree as ET

try:
    import ctypes
except ImportError:
    ctypes = None

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_APPCERT = Path(r"C:\Program Files (x86)\Windows Kits\10\App Certification Kit\appcert.exe")
WACK_REPORT_PREFIX = "wack_preflight_"


@dataclass(frozen=True)
class WackSummary:
    report: str
    overall_result: str
    requirement_count: int
    pass_count: int
    fail_count: int
    warning_count: int


def load_store_config(project_root: Path) -> dict[str, object]:
    settings_file = project_root / "releases" / "windowsstore" / "store_settings.json"
    if settings_file.exists():
        try:
            return json.loads(settings_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    pkg_file = project_root / "store_package.json"
    if pkg_file.exists():
        try:
            return json.loads(pkg_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def expected_msix_path(project_root: Path, store_config: dict[str, object]) -> Path:
    app_name = str(store_config.get("app_name") or "UniversalDocsGrabber")
    candidate_dirs = [
        project_root / "releases" / "windowsstore",
        project_root / "dist",
        Path(r"C:\_Local_DEV\codex_build\universaldocsgrabber\dist"),
    ]
    for directory in candidate_dirs:
        candidate = directory / f"{app_name}.msix"
        if candidate.exists() and candidate.stat().st_size > 0:
            return candidate
    return candidate_dirs[0] / f"{app_name}.msix"


def find_appcert(explicit_path: Path | None = None) -> Path | None:
    if explicit_path is not None:
        candidate = explicit_path.expanduser().resolve()
        if candidate.exists():
            return candidate
        return None

    for tool in ("appcert.exe", "appcert"):
        found = shutil.which(tool)
        if found:
            return Path(found).resolve()

    if DEFAULT_APPCERT.exists():
        return DEFAULT_APPCERT.resolve()

    sdk_base = Path(r"C:\Program Files (x86)\Windows Kits\10")
    if sdk_base.exists():
        for candidate in sdk_base.rglob("appcert.exe"):
            return candidate.resolve()
    return None


def is_windows_admin() -> bool:
    if ctypes is None:
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def resolve_msix_path(project_root: Path, store_config: dict[str, object], explicit: Path | None = None) -> Path:
    return (explicit or expected_msix_path(project_root, store_config)).expanduser().resolve()


def resolve_report_path(project_root: Path, report_dir: Path | None = None, explicit: Path | None = None) -> Path:
    if explicit is not None:
        return explicit.expanduser().resolve()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    directory = (report_dir or project_root / "releases" / "windowsstore" / "test_reports").expanduser().resolve()
    return directory / f"{WACK_REPORT_PREFIX}{timestamp}.xml"


def build_test_command(appcert: Path, msix_path: Path, report_path: Path) -> list[str]:
    return [str(appcert), "test", "-appxpackagepath", str(msix_path), "-reportoutputpath", str(report_path)]


def build_reset_command(appcert: Path) -> list[str]:
    return [str(appcert), "reset"]


def build_finalize_command(appcert: Path, report_path: Path) -> list[str]:
    return [str(appcert), "finalizereport", "-reportfilepath", str(report_path)]


def format_command(command: Sequence[str]) -> str:
    return subprocess.list2cmdline(list(command))


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1].upper()


def _child_text(element: ET.Element, name: str) -> str:
    expected = name.upper()
    for child in list(element):
        if _local_name(child.tag) == expected:
            return (child.text or "").strip()
    return ""


def _iter_named(element: ET.Element, name: str) -> list[ET.Element]:
    expected = name.upper()
    return [node for node in element.iter() if _local_name(node.tag) == expected]


def _result_value(element: ET.Element) -> str:
    attrib_lower = {k.lower(): v for k, v in element.attrib.items()}
    return (
        _child_text(element, "OVERALL_RESULT")
        or _child_text(element, "RESULT")
        or attrib_lower.get("overall_result", "")
        or attrib_lower.get("result", "")
    ).strip().upper()


def parse_wack_report(report_path: Path) -> WackSummary:
    root = ET.parse(report_path).getroot()
    overall = _result_value(root) or "UNKNOWN"
    counts = {"PASS": 0, "FAIL": 0, "WARNING": 0}

    requirements = _iter_named(root, "REQUIREMENT")
    units = requirements if requirements else _iter_named(root, "TEST")

    for unit in units:
        result = _result_value(unit)
        if result in counts:
            counts[result] += 1

    return WackSummary(
        report=str(report_path),
        overall_result=overall,
        requirement_count=len(units),
        pass_count=counts["PASS"],
        fail_count=counts["FAIL"],
        warning_count=counts["WARNING"],
    )


def write_summary(summary: WackSummary, summary_path: Path, *, exit_code: int) -> Path:
    payload = asdict(summary)
    payload["exit_code"] = exit_code
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary_path


def run_command(command: Sequence[str], log_path: Path) -> int:
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except OSError as exc:
        with log_path.open("a", encoding="utf-8") as handle:
            handle.write(f"\n$ {format_command(command)}\n")
            handle.write(f"[BLOCKER] Befehl konnte nicht gestartet werden: {exc}\n")
        print(f"[BLOCKER] Befehl konnte nicht gestartet werden: {exc}", file=sys.stderr)
        return getattr(exc, "winerror", None) or exc.errno or 1

    with log_path.open("a", encoding="utf-8") as handle:
        handle.write(f"\n$ {format_command(command)}\n")
        if completed.stdout:
            handle.write(completed.stdout)
            if not completed.stdout.endswith("\n"):
                handle.write("\n")
        if completed.stderr:
            handle.write(completed.stderr)
            if not completed.stderr.endswith("\n"):
                handle.write("\n")
        handle.write(f"Exit code: {completed.returncode}\n")
    if completed.stdout:
        print(completed.stdout.rstrip())
    if completed.stderr:
        print(completed.stderr.rstrip(), file=sys.stderr)
    return completed.returncode


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Führt WACK für das lokale UniversalDocsGrabber-MSIX aus.")
    parser.add_argument("--project-root", type=Path, default=PROJECT_ROOT, help="Projektordner, Standard: aktuelles Repo.")
    parser.add_argument("--msix", type=Path, help="Pfad zum MSIX, Standard: releases/windowsstore/UniversalDocsGrabber.msix.")
    parser.add_argument("--appcert", type=Path, help="Pfad zu appcert.exe, wenn nicht im Standardpfad.")
    parser.add_argument("--report-dir", type=Path, help="Report-Verzeichnis, Standard: releases/windowsstore/test_reports.")
    parser.add_argument("--report-path", type=Path, help="Expliziter XML-Reportpfad.")
    parser.add_argument("--parse-report", type=Path, help="Vorhandenen WACK-XML-Report auswerten und JSON schreiben.")
    parser.add_argument("--dry-run", action="store_true", help="Pfade und WACK-Befehl anzeigen, nichts ausführen.")
    parser.add_argument("--allow-non-admin", action="store_true", help="WACK trotz fehlender Admin-Erkennung starten.")
    parser.add_argument("--skip-reset", action="store_true", help="appcert reset vor dem Test auslassen.")
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    if args.parse_report:
        report_path = args.parse_report.expanduser().resolve()
        summary = parse_wack_report(report_path)
        summary_path = report_path.with_suffix(".json")
        write_summary(summary, summary_path, exit_code=0)
        print(json.dumps(asdict(summary), ensure_ascii=False, indent=2))
        print(f"WACK-Zusammenfassung: {summary_path}")
        return 0 if summary.fail_count == 0 and summary.overall_result != "FAIL" else 1

    project_root = args.project_root.resolve()
    store_config = load_store_config(project_root)
    msix_path = resolve_msix_path(project_root, store_config, args.msix)
    report_path = resolve_report_path(project_root, args.report_dir, args.report_path)
    log_path = report_path.with_suffix(".log")
    summary_path = report_path.with_suffix(".json")
    appcert = find_appcert(args.appcert)

    print(f"MSIX: {msix_path}")
    print(f"WACK-Report: {report_path}")
    print(f"WACK-Log: {log_path}")
    if appcert is None:
        print("AppCert: nicht gefunden")
    else:
        print(f"AppCert: {appcert}")
        print(f"Befehl: {format_command(build_test_command(appcert, msix_path, report_path))}")

    if args.dry_run:
        return 0

    errors: list[str] = []
    if appcert is None:
        errors.append("appcert.exe fehlt. Windows App Certification Kit installieren oder --appcert setzen.")
    if not msix_path.exists() or msix_path.stat().st_size == 0:
        errors.append(f"MSIX fehlt oder ist leer: {msix_path}")
    if not args.allow_non_admin and not is_windows_admin():
        errors.append("WACK sollte als Administrator laufen. Nutze eine erhöhte PowerShell oder --allow-non-admin.")

    if errors:
        for error in errors:
            print(f"[BLOCKER] {error}", file=sys.stderr)
        return 2

    assert appcert is not None
    report_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(
        f"WACK gestartet: {datetime.now().isoformat(timespec='seconds')}\nMSIX: {msix_path}\nReport: {report_path}\n",
        encoding="utf-8",
    )

    if not args.skip_reset:
        reset_exit = run_command(build_reset_command(appcert), log_path)
        if reset_exit == 740:
            print("[BLOCKER] appcert reset verlangt erhöhte Rechte.", file=sys.stderr)
            return 2

    exit_code = run_command(build_test_command(appcert, msix_path, report_path), log_path)
    if exit_code == 740:
        print("[BLOCKER] appcert test verlangt erhöhte Rechte.", file=sys.stderr)
        return 2
    if report_path.exists():
        run_command(build_finalize_command(appcert, report_path), log_path)
        summary = parse_wack_report(report_path)
        write_summary(summary, summary_path, exit_code=exit_code)
        print(
            "WACK-Ergebnis: "
            f"{summary.overall_result}, {summary.pass_count} PASS, "
            f"{summary.fail_count} FAIL, {summary.warning_count} WARNING"
        )
        print(f"WACK-Zusammenfassung: {summary_path}")
        if summary.fail_count > 0 or summary.overall_result == "FAIL":
            return 1
        return 0 if exit_code in (0, 1) else exit_code

    print("[BLOCKER] WACK hat keinen XML-Report erzeugt.", file=sys.stderr)
    return exit_code if exit_code != 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
