#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI & Automation Interface for UniversalDocsGrabber
===================================================

Provides a headless command-line interface for UniversalDocsGrabber to enable
automation, background scheduling, document indexing, library export, and stack
diagnostics without requiring a GUI display server.

Features:
- Version inquiry (--version / -v)
- List configured search profiles (--list-profiles)
- List configured mail accounts (--list-accounts)
- List downloaded documents with filtering (--list-documents [--profile NAME] [--category NAME] [--limit N])
- Headless redacted library export (--export-library [PATH])
- Headless CSV document export (--export-csv [PATH])
- Runtime stack diagnostics (--diagnose / --check-stack)
- Structured JSON output (--json) for seamless tool/script/agent integration
- Custom config and database paths (--config, --documents-db)
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Set, Tuple

APP_NAME = "UniversalDocsGrabber"
VERSION = "1.1.7"

DEFAULT_BASE_DIR = Path.home() / ".univ_docs_grabber"
DEFAULT_CONFIG_FILE = DEFAULT_BASE_DIR / "config_v1.json"
DEFAULT_DOCS_DB = DEFAULT_BASE_DIR / "documents.json"
DEFAULT_LIBRARY_EXPORT = DEFAULT_BASE_DIR / "docsgrabber-library-v1.json"
DEFAULT_CSV_EXPORT = DEFAULT_BASE_DIR / "documents_export.csv"

EXPORT_SCHEMA = "docsgrabber-library-v1"
EXPORT_SCHEMA_VERSION = "1.0.0"
DEFAULT_GROUP = "Allgemein"

_RESERVED_DEVICE_NAMES: Set[str] = {
    "CON", "PRN", "AUX", "NUL", "CLOCK$",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
}


def get_default_paths(config_path: Optional[str] = None, db_path: Optional[str] = None) -> Tuple[Path, Path]:
    """Returns resolved config and documents database paths."""
    c_path = Path(config_path).resolve() if config_path else DEFAULT_CONFIG_FILE
    d_path = Path(db_path).resolve() if db_path else DEFAULT_DOCS_DB
    return c_path, d_path


def sanitize_filename(name: str) -> str:
    """Sanitizes filename for cross-platform filesystem safety and limits length."""
    if not name or not isinstance(name, str):
        return "unnamed"
    s = re.sub(r'[^\w\s\.-]', '', name)
    s = re.sub(r'\s+', '_', s)
    result = s.strip().rstrip('. ')[:100].rstrip('. ')
    if not result:
        return "unnamed"
    stem = result.split(".")[0].upper()
    if result.upper() in _RESERVED_DEVICE_NAMES or stem in _RESERVED_DEVICE_NAMES:
        result = f"file_{result}"
    return result


def build_account_ref(account_name: Optional[str]) -> str:
    """Builds a stable, redacted reference for an email account."""
    if not account_name or not str(account_name).strip():
        return "account-unknown"
    normalized = str(account_name).strip().encode("utf-8")
    digest = hashlib.sha256(normalized).hexdigest()[:12]
    return f"account-{digest}"


def redact_path_hint(path_value: Optional[str], base_path: Path) -> dict:
    """Redacts absolute filesystem paths to relative hints or basenames."""
    if not path_value or not isinstance(path_value, (str, Path)):
        return {"kind": "basename", "value": ""}
    path = Path(path_value)
    try:
        rel_path = path.resolve(strict=False).relative_to(base_path.resolve(strict=False))
        return {"kind": "relative", "value": rel_path.as_posix()}
    except (ValueError, TypeError, OSError):
        return {"kind": "basename", "value": path.name}


def infer_document_category(path_value: Optional[str], base_path: Path, profile_name: str, target_folder: str = "") -> str:
    """Infers an optional category from the document path."""
    if not path_value or not isinstance(path_value, (str, Path)):
        return ""
    profile_folder = sanitize_filename(profile_name or "")
    target_folder_sanitized = sanitize_filename(target_folder) if target_folder else ""
    path = Path(path_value)
    try:
        rel_path = path.resolve(strict=False).relative_to(base_path.resolve(strict=False))
    except (ValueError, TypeError, OSError):
        return ""

    parts = list(rel_path.parts[:-1])
    if len(parts) < 2:
        return ""
    if parts[0] == profile_folder or (target_folder_sanitized and parts[0] == target_folder_sanitized):
        return parts[1]
    return ""


def calculate_file_hash(path: Optional[Path]) -> Optional[str]:
    """Calculates cryptographic SHA-256 hash of a file if available."""
    if not path:
        return None
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except (FileNotFoundError, PermissionError, OSError, TypeError):
        return None


def load_data(
    config_path: Optional[str] = None,
    db_path: Optional[str] = None,
) -> Tuple[str, dict, List[dict], List[dict], int, List[dict]]:
    """Loads configuration, accounts, search profiles, and document database without GUI dependencies."""
    c_path, d_path = get_default_paths(config_path, db_path)

    base_path = str(Path.home() / "Downloads" / "UnivDocs")
    global_settings: dict = {
        "download_attachments": True,
        "convert_body_to_pdf": True,
        "convert_all_to_pdf": False,
        "enable_hash_check": False,
        "auto_categorize": False,
        "category_rules": [],
        "formats": ["pdf", "docx", "doc", "jpg", "png"],
    }
    profiles: List[dict] = []
    accounts: List[dict] = []
    scheduler_interval = 0
    documents: List[dict] = []

    if c_path.exists():
        try:
            data = json.loads(c_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                raw_bp = data.get("base_path")
                if raw_bp and isinstance(raw_bp, str) and raw_bp.strip():
                    base_path = raw_bp.strip()
                loaded_settings = data.get("global_settings", {})
                if isinstance(loaded_settings, dict):
                    global_settings.update(loaded_settings)
                raw_profiles = data.get("profiles", [])
                if isinstance(raw_profiles, list):
                    profiles = [p for p in raw_profiles if isinstance(p, dict)]
                raw_accounts = data.get("accounts", [])
                if isinstance(raw_accounts, list):
                    accounts = [a for a in raw_accounts if isinstance(a, dict)]
                raw_interval = data.get("scheduler_interval")
                if raw_interval is not None:
                    try:
                        scheduler_interval = int(raw_interval)
                    except (ValueError, TypeError):
                        scheduler_interval = 0
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            print(f"[WARNUNG] Konfigurationsdatei konnte nicht vollständig geladen werden: {e}", file=sys.stderr)

    if d_path.exists():
        try:
            raw_docs = json.loads(d_path.read_text(encoding="utf-8"))
            if isinstance(raw_docs, list):
                documents = [d for d in raw_docs if isinstance(d, dict)]
        except (OSError, json.JSONDecodeError, KeyError, ValueError, TypeError) as e:
            print(f"[WARNUNG] Dokumentendatenbank konnte nicht geladen werden: {e}", file=sys.stderr)

    return base_path, global_settings, profiles, accounts, scheduler_interval, documents


def collect_category_entries(
    global_settings: dict,
    profiles: List[dict],
    documents: List[dict],
    base_path: Path,
) -> List[dict]:
    """Collects all known category entries across rules and stored document paths."""
    category_map: Dict[str, Dict[str, Any]] = {}
    profile_target_map = {p.get("name", ""): p.get("target_folder", "") for p in profiles}

    def add_category(name: str, source: str, profile_name: str = ""):
        if not name:
            return
        entry = category_map.setdefault(
            name,
            {"name": name, "sources": set(), "profile_names": set()},
        )
        entry["sources"].add(source)
        if profile_name:
            entry["profile_names"].add(profile_name)

    for rule in global_settings.get("category_rules", []) or []:
        if isinstance(rule, dict):
            add_category(rule.get("folder", ""), "global_rule")

    for profile in profiles:
        prof_name = profile.get("name", "")
        over = profile.get("override_settings")
        settings = over if isinstance(over, dict) else global_settings
        for rule in settings.get("category_rules", []) or []:
            if isinstance(rule, dict):
                add_category(rule.get("folder", ""), "profile_rule", prof_name)

    for doc in documents:
        doc_path = doc.get("path", "")
        doc_prof = doc.get("profile", "")
        target_folder = profile_target_map.get(doc_prof, "")
        cat = infer_document_category(doc_path, base_path, doc_prof, target_folder)
        add_category(cat, "document_path", doc_prof)

    return [
        {
            "name": name,
            "sources": sorted(entry["sources"]),
            "profile_names": sorted(entry["profile_names"]),
        }
        for name, entry in sorted(category_map.items())
    ]


def build_library_export_payload(
    base_path_str: str,
    global_settings: dict,
    profiles: List[dict],
    accounts: List[dict],
    scheduler_interval: int,
    documents: List[dict],
    exported_at: Optional[datetime] = None,
) -> dict:
    """Builds the redacted companion export payload matching docsgrabber-library-v1.json."""
    base_path = Path(base_path_str)
    export_dt = exported_at or datetime.now(timezone.utc).astimezone()
    export_timestamp = export_dt.isoformat(timespec="seconds")

    account_refs = {a.get("name", ""): build_account_ref(a.get("name", "")) for a in accounts}
    profile_target_map = {p.get("name", ""): p.get("target_folder", "") for p in profiles}

    documents_by_profile: Dict[str, List[dict]] = {}
    exported_documents: List[dict] = []

    for doc in documents:
        raw_path = doc.get("path") or ""
        doc_path = Path(raw_path) if raw_path else None
        exists = doc_path.exists() if doc_path else False
        prof_name = doc.get("profile") or ""
        target_folder = profile_target_map.get(prof_name, "")
        category = infer_document_category(raw_path, base_path, prof_name, target_folder)

        exported_doc = {
            "profile_name": prof_name,
            "filename": doc.get("filename") or "",
            "document_date": doc.get("date") or "",
            "file_type": doc_path.suffix.lower().lstrip(".") if doc_path else "",
            "category": category or None,
            "path_hint": redact_path_hint(raw_path, base_path),
            "status": "available" if exists else "missing",
            "sha256": calculate_file_hash(doc_path) if exists and doc_path else None,
        }
        exported_documents.append(exported_doc)
        documents_by_profile.setdefault(prof_name, []).append(exported_doc)

    exported_profiles = []
    profile_stats = []

    for p in profiles:
        prof_name = p.get("name", "")
        over = p.get("override_settings")
        effective_settings = over if isinstance(over, dict) else global_settings
        profile_docs = documents_by_profile.get(prof_name, [])
        last_doc_date = max((d["document_date"] for d in profile_docs if d.get("document_date")), default=None)

        acc_name = p.get("account_name", "")
        acc_ref = account_refs.get(acc_name, build_account_ref(acc_name))

        exported_profiles.append({
            "id": p.get("id", ""),
            "name": prof_name,
            "group": p.get("group", DEFAULT_GROUP) or DEFAULT_GROUP,
            "active": bool(p.get("active", True)),
            "account_ref": acc_ref,
            "target_folder": p.get("target_folder", ""),
            "filters": {
                "subject": p.get("query_subject", ""),
                "sender": p.get("query_sender", ""),
                "since": p.get("query_since", ""),
                "gmail_query": p.get("gmail_query", ""),
            },
            "effective_settings": {
                "download_attachments": bool(effective_settings.get("download_attachments", True)),
                "convert_body_to_pdf": bool(effective_settings.get("convert_body_to_pdf", True)),
                "convert_all_to_pdf": bool(effective_settings.get("convert_all_to_pdf", False)),
                "enable_hash_check": bool(effective_settings.get("enable_hash_check", False)),
                "auto_categorize": bool(effective_settings.get("auto_categorize", False)),
                "category_rule_count": len(effective_settings.get("category_rules", []) or []),
                "formats": list(effective_settings.get("formats", []) or []),
            },
            "document_count": len(profile_docs),
            "last_document_date": last_doc_date,
        })

        profile_stats.append({
            "profile_name": prof_name,
            "document_count": len(profile_docs),
            "last_document_date": last_doc_date,
            "active": bool(p.get("active", True)),
        })

    exported_accounts = [
        {
            "ref": account_refs.get(a.get("name", ""), build_account_ref(a.get("name", ""))),
            "profile_count": sum(1 for p in profiles if p.get("account_name") == a.get("name")),
        }
        for a in accounts
    ]

    categories = collect_category_entries(global_settings, profiles, documents, base_path)

    return {
        "schema": EXPORT_SCHEMA,
        "schema_version": EXPORT_SCHEMA_VERSION,
        "app": {
            "name": APP_NAME,
            "version": VERSION,
            "exported_at": export_timestamp,
        },
        "capabilities": {
            "redacted": True,
            "contains_credentials": False,
            "contains_document_files": False,
            "contains_mail_body_text": False,
        },
        "base_path_hint": {
            "kind": "basename",
            "value": Path(base_path).name,
        },
        "accounts": exported_accounts,
        "profiles": exported_profiles,
        "categories": categories,
        "documents": exported_documents,
        "run_summary": {
            "exported_profile_count": len(exported_profiles),
            "active_profile_count": sum(1 for p in profiles if p.get("active", True)),
            "exported_document_count": len(exported_documents),
            "scheduler_interval_minutes": scheduler_interval,
            "profile_stats": profile_stats,
        },
    }


def export_documents_to_csv(
    documents: List[dict],
    output_path: Path,
    profile_filter: Optional[str] = None,
    category_filter: Optional[str] = None,
    base_path_str: Optional[str] = None,
    profiles: Optional[List[dict]] = None,
) -> int:
    """Exports document records to a semicolon-separated CSV file with UTF-8 BOM."""
    base_path = Path(base_path_str) if (base_path_str and str(base_path_str).strip()) else Path.home() / "Downloads" / "UnivDocs"
    profile_target_map = {p.get("name", ""): p.get("target_folder", "") for p in (profiles or []) if isinstance(p, dict)}

    resolved_path = Path(output_path).resolve() if output_path else DEFAULT_CSV_EXPORT
    if str(output_path).strip() in ("", "."):
        resolved_path = Path.cwd() / "documents_export.csv"
    elif resolved_path.is_dir():
        resolved_path = resolved_path / "documents_export.csv"

    resolved_path.parent.mkdir(parents=True, exist_ok=True)
    count = 0

    import os
    temp_path = resolved_path.parent / f".tmp_{resolved_path.name}_{int(time.time() * 1000)}"
    try:
        with open(temp_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["Datum", "Profil", "Kategorie", "Dateiname", "Pfad", "Absender", "Betreff"])

            for doc in documents:
                prof = doc.get("profile") or ""
                if profile_filter and prof.lower() != profile_filter.lower():
                    continue

                raw_path = doc.get("path") or ""
                target_folder = profile_target_map.get(prof, "")
                cat = infer_document_category(raw_path, base_path, prof, target_folder)
                if category_filter and (cat or "").lower() != category_filter.lower():
                    continue

                writer.writerow([
                    doc.get("date") or "",
                    prof,
                    cat or "",
                    doc.get("filename") or "",
                    raw_path,
                    doc.get("sender") or "",
                    doc.get("subject") or "",
                ])
                count += 1
        os.replace(temp_path, resolved_path)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except OSError:
                pass

    return count


def check_system_stack(base_path_str: Optional[str] = None) -> dict:
    """Performs runtime diagnostics of all document processing, OCR, and conversion backends."""
    stack: Dict[str, Any] = {}

    # 1. HTML -> PDF (xhtml2pdf / pisa)
    try:
        import xhtml2pdf  # noqa: F401
        stack["xhtml2pdf"] = {"available": True, "status": "OK"}
    except ImportError:
        stack["xhtml2pdf"] = {"available": False, "status": "Missing (Body-to-PDF disabled)"}

    # 2. OCR (pytesseract)
    try:
        import pytesseract
        tess_version = getattr(pytesseract, "__version__", "available")
        stack["pytesseract"] = {"available": True, "version": str(tess_version), "status": "OK"}
    except ImportError:
        stack["pytesseract"] = {"available": False, "status": "Missing (OCR disabled)"}

    # 3. PDF Rasterization (pdf2image & poppler)
    try:
        import pdf2image  # noqa: F401
        poppler_found = bool(shutil.which("pdftoppm"))
        stack["pdf2image"] = {
            "available": True,
            "poppler_in_path": poppler_found,
            "status": "OK" if poppler_found else "pdf2image installed, but poppler not in PATH",
        }
    except ImportError:
        stack["pdf2image"] = {"available": False, "status": "Missing (Scanned PDF OCR disabled)"}

    # 4. PDF Manipulation (pypdf)
    try:
        import pypdf
        pypdf_ver = getattr(pypdf, "__version__", "available")
        stack["pypdf"] = {"available": True, "version": str(pypdf_ver), "status": "OK"}
    except ImportError:
        stack["pypdf"] = {"available": False, "status": "Missing (PDF merging/parsing disabled)"}

    # 5. TXT -> PDF (reportlab)
    try:
        import reportlab
        rl_ver = getattr(reportlab, "__version__", "available")
        stack["reportlab"] = {"available": True, "version": str(rl_ver), "status": "OK"}
    except ImportError:
        stack["reportlab"] = {"available": False, "status": "Missing (Text-to-PDF disabled)"}

    # 6. Images (Pillow)
    try:
        from PIL import Image
        pil_ver = getattr(Image, "__version__", "available")
        stack["pillow"] = {"available": True, "version": str(pil_ver), "status": "OK"}
    except ImportError:
        stack["pillow"] = {"available": False, "status": "Missing (Image-to-PDF disabled)"}

    # 7. Word / Office -> PDF (win32com / docx2pdf)
    has_win32 = False
    try:
        import win32com.client  # noqa: F401
        has_win32 = True
    except ImportError:
        pass

    has_docx2pdf = False
    try:
        import docx2pdf  # noqa: F401
        has_docx2pdf = True
    except ImportError:
        pass

    stack["office_conversion"] = {
        "win32com": has_win32,
        "docx2pdf": has_docx2pdf,
        "status": "OK (win32com)" if has_win32 else ("Fallback (docx2pdf)" if has_docx2pdf else "Office conversion not available"),
    }

    # 8. Storage Directory
    target_dir = Path(base_path_str).resolve() if (base_path_str and str(base_path_str).strip()) else (Path.home() / "Downloads" / "UnivDocs")
    writable = False
    test_file = None
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        test_file = target_dir / f".write_test_{int(time.time() * 1000)}.tmp"
        test_file.write_text("ok", encoding="utf-8")
        writable = True
    except Exception:
        writable = False
    finally:
        if test_file and test_file.exists():
            try:
                test_file.unlink()
            except OSError:
                pass

    stack["storage"] = {
        "path": str(target_dir),
        "exists": target_dir.exists(),
        "writable": writable,
    }

    return {
        "app": APP_NAME,
        "version": VERSION,
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "components": stack,
        "ready": bool(stack["pypdf"]["available"] and stack["pillow"]["available"] and writable),
    }


def build_parser() -> argparse.ArgumentParser:
    """Constructs the argument parser for UniversalDocsGrabber CLI."""
    parser = argparse.ArgumentParser(
        prog="universaldocsgrabber",
        description=f"{APP_NAME} v{VERSION} - Headless CLI & Automation Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"{APP_NAME} {VERSION}",
    )
    parser.add_argument(
        "--config",
        dest="config_path",
        metavar="PFAD",
        help="Pfad zur alternativen config_v1.json Datei.",
    )
    parser.add_argument(
        "--documents-db",
        dest="documents_db_path",
        metavar="PFAD",
        help="Pfad zur alternativen documents.json Datei.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        help="Gibt Ausgaben als strukturiertes JSON auf stdout aus.",
    )

    action_group = parser.add_mutually_exclusive_group()
    action_group.add_argument(
        "--list-profiles",
        action="store_true",
        help="Listet alle konfigurierten Suchprofile auf.",
    )
    action_group.add_argument(
        "--list-accounts",
        action="store_true",
        help="Listet alle konfigurierten E-Mail-Konten auf (Passwörter maskiert).",
    )
    action_group.add_argument(
        "--list-documents",
        action="store_true",
        help="Listet erfasste Dokumente auf.",
    )
    action_group.add_argument(
        "--export-library",
        nargs="?",
        const="DEFAULT",
        metavar="ZIELPFAD",
        help="Exportiert den redigierten PWA/Web-Companion-Katalog (docsgrabber-library-v1.json).",
    )
    action_group.add_argument(
        "--export-csv",
        nargs="?",
        const="DEFAULT",
        metavar="ZIELPFAD",
        help="Exportiert Dokumente in eine CSV-Datei (Default: ~/.univ_docs_grabber/documents_export.csv).",
    )
    action_group.add_argument(
        "--diagnose", "--check-stack",
        action="store_true",
        dest="diagnose",
        help="Führt System- & Stack-Diagnose (Poppler, OCR, xhtml2pdf, Word) aus.",
    )
    action_group.add_argument(
        "--gui",
        action="store_true",
        help="Startet die grafische Benutzeroberfläche (Standard bei Aufruf ohne Flags).",
    )

    # Filter-Optionen für List- und Export-Befehle
    parser.add_argument(
        "--profile",
        dest="filter_profile",
        metavar="NAME",
        help="Filtert Dokumente nach Profil-Name.",
    )
    parser.add_argument(
        "--category",
        dest="filter_category",
        metavar="NAME",
        help="Filtert Dokumente nach Kategorie.",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        metavar="ANZAHL",
        help="Maximale Anzahl Dokumente bei --list-documents (Standard: 50, 0 = unbegrenzt).",
    )

    return parser


def has_cli_action(argv: Optional[Sequence[str]] = None) -> bool:
    """Checks whether the argument list contains a command-line action."""
    if argv is None:
        argv = sys.argv[1:]
    if not argv:
        return False

    cli_triggers = {
        "-h", "--help",
        "-v", "--version",
        "--list-profiles",
        "--list-accounts",
        "--list-documents",
        "--export-library",
        "--export-csv",
        "--diagnose", "--check-stack",
    }
    for arg in argv:
        clean_arg = arg.split("=")[0]
        if clean_arg in cli_triggers:
            return True
    return False


def run_cli(argv: Optional[Sequence[str]] = None) -> int:
    """Main CLI execution router."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.gui:
        return -1  # Signal to caller to launch GUI

    base_path, global_settings, profiles, accounts, scheduler_interval, documents = load_data(
        config_path=args.config_path,
        db_path=args.documents_db_path,
    )

    # 1. Profile auflisten
    if args.list_profiles:
        if args.json_output:
            print(json.dumps(profiles, indent=2, ensure_ascii=False))
            return 0
        print(f"Konfigurierte Suchprofile ({len(profiles)}):")
        print("-" * 75)
        for p in profiles:
            p_name = p.get("name", "Unbenannt")
            p_group = p.get("group", DEFAULT_GROUP) or DEFAULT_GROUP
            p_acc = p.get("account_name", "-")
            p_subj = p.get("query_subject", "*")
            p_en = "Aktiv" if p.get("active", True) else "Inaktiv"
            print(f"• [{p_en}] {p_name:<20} | Gruppe: {p_group:<12} | Account: {p_acc:<15} | Betreff: {p_subj}")
        return 0

    # 2. Accounts auflisten
    if args.list_accounts:
        # Passwörter strikt maskieren / entfernen
        safe_accounts = []
        for a in accounts:
            safe_acc = dict(a)
            if "password" in safe_acc:
                safe_acc["password"] = "***MASKED***"
            safe_accounts.append(safe_acc)

        if args.json_output:
            print(json.dumps(safe_accounts, indent=2, ensure_ascii=False))
            return 0
        print(f"Konfigurierte E-Mail-Konten ({len(accounts)}):")
        print("-" * 75)
        for a in safe_accounts:
            a_name = a.get("name", "Unbenannt")
            a_host = a.get("host", "localhost")
            a_user = a.get("user", "")
            a_folder = a.get("search_folder", "INBOX")
            print(f"• {a_name:<20} | Host: {a_host:<20} | User: {a_user:<25} | Ordner: {a_folder}")
        return 0

    # 3. Dokumente auflisten
    if args.list_documents:
        filtered = documents
        if args.filter_profile:
            filtered = [d for d in filtered if (d.get("profile") or "").lower() == args.filter_profile.lower()]

        if args.filter_category:
            base_p = Path(base_path)
            profile_target_map = {p.get("name", ""): p.get("target_folder", "") for p in profiles if isinstance(p, dict)}
            filtered = [
                d for d in filtered
                if (infer_document_category(d.get("path") or "", base_p, d.get("profile") or "", profile_target_map.get(d.get("profile") or "", "")) or "").lower() == args.filter_category.lower()
            ]

        total_matching = len(filtered)
        if args.limit and args.limit > 0:
            filtered = filtered[:args.limit]

        if args.json_output:
            out_obj = {
                "total_count": total_matching,
                "returned_count": len(filtered),
                "documents": filtered,
            }
            print(json.dumps(out_obj, indent=2, ensure_ascii=False))
            return 0

        print(f"Erfasste Dokumente ({len(filtered)} von {total_matching}):")
        print("-" * 75)
        for doc in filtered:
            d_date = doc.get("date") or "-"
            d_prof = doc.get("profile") or "-"
            d_file = doc.get("filename") or "-"
            print(f"• {d_date} | {d_prof:<18} | {d_file}")
        return 0

    # 4. Redigierten Library-Export erzeugen
    if args.export_library is not None:
        payload = build_library_export_payload(
            base_path_str=base_path,
            global_settings=global_settings,
            profiles=profiles,
            accounts=accounts,
            scheduler_interval=scheduler_interval,
            documents=documents,
        )

        raw_target = args.export_library
        if raw_target == "DEFAULT" or not raw_target or not str(raw_target).strip():
            out_path = DEFAULT_LIBRARY_EXPORT
        else:
            p = Path(raw_target).resolve()
            if p.is_dir() or str(raw_target).strip() in ("", "."):
                out_path = p / "docsgrabber-library-v1.json" if p.is_dir() else Path.cwd() / "docsgrabber-library-v1.json"
            else:
                out_path = p

        import os
        out_path.parent.mkdir(parents=True, exist_ok=True)
        temp_out = out_path.parent / f".tmp_{out_path.name}_{int(time.time() * 1000)}"
        try:
            temp_out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
            os.replace(temp_out, out_path)
        except OSError as e:
            if args.json_output:
                print(json.dumps({"status": "error", "message": str(e)}, indent=2, ensure_ascii=False))
            else:
                print(f"[FEHLER] Library-Export fehlgeschlagen: {e}", file=sys.stderr)
            return 1
        finally:
            if temp_out.exists():
                try:
                    temp_out.unlink()
                except OSError:
                    pass

        if args.json_output:
            print(json.dumps({
                "status": "success",
                "output_path": str(out_path),
                "profiles": payload["run_summary"]["exported_profile_count"],
                "documents": payload["run_summary"]["exported_document_count"],
            }, indent=2, ensure_ascii=False))
        else:
            print(f"Redigierter Companion-Export gespeichert: {out_path}")
            print(f"Exportierte Profile: {payload['run_summary']['exported_profile_count']} | Dokumente: {payload['run_summary']['exported_document_count']}")
        return 0

    # 5. CSV Export
    if args.export_csv is not None:
        raw_target = args.export_csv
        if raw_target == "DEFAULT" or not raw_target or not str(raw_target).strip():
            out_path = DEFAULT_CSV_EXPORT
        else:
            p = Path(raw_target).resolve()
            if p.is_dir() or str(raw_target).strip() in ("", "."):
                out_path = p / "documents_export.csv" if p.is_dir() else Path.cwd() / "documents_export.csv"
            else:
                out_path = p

        try:
            count = export_documents_to_csv(
                documents=documents,
                output_path=out_path,
                profile_filter=args.filter_profile,
                category_filter=args.filter_category,
                base_path_str=base_path,
                profiles=profiles,
            )
        except OSError as e:
            if args.json_output:
                print(json.dumps({"status": "error", "message": str(e)}, indent=2, ensure_ascii=False))
            else:
                print(f"[FEHLER] CSV-Export fehlgeschlagen: {e}", file=sys.stderr)
            return 1

        if args.json_output:
            print(json.dumps({
                "status": "success",
                "output_path": str(out_path),
                "exported_count": count,
            }, indent=2, ensure_ascii=False))
        else:
            print(f"CSV-Export erfolgreich gespeichert: {out_path} ({count} Einträge)")
        return 0

    # 6. Stack-Diagnose
    if args.diagnose:
        report = check_system_stack(base_path_str=base_path)
        if args.json_output:
            print(json.dumps(report, indent=2, ensure_ascii=False))
            return 0 if report["ready"] else 1

        print(f"System- & Stack-Diagnose für {APP_NAME} v{VERSION}:")
        print("-" * 75)
        for comp, info in report["components"].items():
            st = info.get("status", "OK" if info.get("available") else "Missing")
            print(f"• {comp:<20}: {st}")
        print("-" * 75)
        print(f"Gesamtstatus: {'BEREIT' if report['ready'] else 'EINGESCHRÄNKT / PRÜFUNG ERFORDERLICH'}")
        return 0 if report["ready"] else 1

    # Fallback: Kein Schalter angegeben -> GUI starten
    return -1


if __name__ == "__main__":
    res = run_cli(sys.argv[1:])
    if res == -1:
        # GUI anfordern
        try:
            from UniversalDocsGrabberV1 import main as app_main
            sys.exit(app_main(["--gui"]))
        except ImportError:
            print("[INFO] Kein CLI-Befehl angegeben. Starte GUI...", file=sys.stderr)
            sys.exit(0)
    sys.exit(res)
