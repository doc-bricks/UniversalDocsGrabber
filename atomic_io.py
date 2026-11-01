# -*- coding: utf-8 -*-
"""
Atomic and fail-safe file I/O operations for UniversalDocsGrabber.
=================================================================
Provides collision-free temporary file writes, explicit fsync durability guarantees,
Windows read-only attribute handling, cleanup guards on failure, and protection
against accidental overwrites of internal database and configuration files.

Referenz: Policy P-006 / Local-First Data Integrity Architecture
"""

from __future__ import annotations

import json
import os
import stat
import uuid
from pathlib import Path
from typing import Any, Iterable, Optional, Set


def resolve_path(path: str | Path) -> Path:
    """Resolve a path to its normalized absolute representation."""
    p = Path(path).expanduser()
    try:
        return p.resolve()
    except (OSError, RuntimeError):
        return p.absolute()


def is_protected_path(target: str | Path, protected_paths: Iterable[str | Path] | None) -> bool:
    """Check whether target matches or aliases any protected path."""
    if not protected_paths:
        return False
    target_resolved = resolve_path(target)
    for protected in protected_paths:
        if protected is None:
            continue
        try:
            prot_resolved = resolve_path(protected)
            if target_resolved == prot_resolved:
                return True
            if target_resolved.exists() and prot_resolved.exists():
                try:
                    if os.path.samefile(target_resolved, prot_resolved):
                        return True
                except (OSError, ValueError):
                    pass
        except (OSError, RuntimeError, ValueError):
            continue
    return False


def get_default_protected_paths(base_dir: Optional[Path] = None) -> Set[Path]:
    """Return the set of protected internal data and configuration paths.

    Protects config_v1.json and documents.json in both the provided base_dir
    and the user's default .univ_docs_grabber directory.
    """
    default_user_dir = Path.home() / ".univ_docs_grabber"
    protected: Set[Path] = {
        resolve_path(default_user_dir / "config_v1.json"),
        resolve_path(default_user_dir / "documents.json"),
        resolve_path(default_user_dir / "token.json"),
    }
    if base_dir is not None:
        base_resolved = resolve_path(base_dir)
        protected.add(resolve_path(base_resolved / "config_v1.json"))
        protected.add(resolve_path(base_resolved / "documents.json"))
        protected.add(resolve_path(base_resolved / "token.json"))
    return protected


def atomic_write_text(
    target: str | Path,
    text: str,
    encoding: str = "utf-8",
    errors: Optional[str] = None,
    newline: Optional[str] = None,
    protected_paths: Iterable[str | Path] | None = None,
) -> Path:
    """Atomically write text content to target file.

    Guarantees:
    - Pre-flight rejection of protected files (e.g. internal storage databases).
    - Writes to a unique per-process/UUID temp file in the target directory.
    - Explicit flush and fsync for crash durability.
    - Windows read-only permission reset prior to atomic replace.
    - Automatic cleanup of temporary file on error.
    - Preserves existing target file untouched if writing or replace fails.
    """
    target_path = resolve_path(target)
    if target_path.is_dir():
        raise IsADirectoryError(f"Zielpfad '{target_path}' ist ein existierendes Verzeichnis.")
    if is_protected_path(target_path, protected_paths):
        raise PermissionError(
            f"Zielpfad '{target_path}' darf keine geschützte Konfigurations- oder Datenbankdatei überschreiben."
        )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_name(
        f".{target_path.name}.tmp.{os.getpid()}_{uuid.uuid4().hex[:8]}"
    )

    try:
        with open(tmp_path, "w", encoding=encoding, errors=errors, newline=newline) as f:
            f.write(text)
            f.flush()
            try:
                os.fsync(f.fileno())
            except (OSError, AttributeError):
                pass

        if target_path.exists():
            try:
                os.chmod(target_path, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass

        os.replace(tmp_path, target_path)
        return target_path
    finally:
        if tmp_path.exists():
            try:
                os.chmod(tmp_path, stat.S_IWRITE | stat.S_IREAD)
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass


def atomic_write_bytes(
    target: str | Path,
    data: bytes,
    protected_paths: Iterable[str | Path] | None = None,
    min_bytes: int = 0,
) -> Path:
    """Atomically write binary data to target file with non-emptiness validation."""
    if len(data) < min_bytes:
        raise ValueError(f"Binärdaten sind unvollständig ({len(data)} Bytes < {min_bytes} Bytes)")

    target_path = resolve_path(target)
    if target_path.is_dir():
        raise IsADirectoryError(f"Zielpfad '{target_path}' ist ein existierendes Verzeichnis.")
    if is_protected_path(target_path, protected_paths):
        raise PermissionError(
            f"Zielpfad '{target_path}' darf keine geschützte Konfigurations- oder Datenbankdatei überschreiben."
        )

    target_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = target_path.with_name(
        f".{target_path.name}.tmp.{os.getpid()}_{uuid.uuid4().hex[:8]}"
    )

    try:
        with open(tmp_path, "wb") as f:
            f.write(data)
            f.flush()
            try:
                os.fsync(f.fileno())
            except (OSError, AttributeError):
                pass

        if target_path.exists():
            try:
                os.chmod(target_path, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass

        os.replace(tmp_path, target_path)
        return target_path
    finally:
        if tmp_path.exists():
            try:
                os.chmod(tmp_path, stat.S_IWRITE | stat.S_IREAD)
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass


def atomic_write_json(
    target: str | Path,
    data: Any,
    indent: int = 2,
    ensure_ascii: bool = False,
    encoding: str = "utf-8",
    protected_paths: Iterable[str | Path] | None = None,
) -> Path:
    """Atomically serialize and write JSON data to target file.

    Serializes to memory first to avoid touching the disk if serialization fails.
    """
    text = json.dumps(data, ensure_ascii=ensure_ascii, indent=indent) + "\n"
    return atomic_write_text(
        target,
        text,
        encoding=encoding,
        protected_paths=protected_paths,
    )


def atomic_publish_file(
    source_tmp: str | Path,
    target: str | Path,
    protected_paths: Iterable[str | Path] | None = None,
    min_bytes: int = 0,
) -> Path:
    """Publish an already generated temporary file to target atomically.

    Verifies non-emptiness (min_bytes) and cleans up source_tmp on failure.
    """
    tmp_path = Path(source_tmp)
    target_path = resolve_path(target)

    if target_path.is_dir():
        if tmp_path.exists():
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise IsADirectoryError(f"Zielpfad '{target_path}' ist ein existierendes Verzeichnis.")

    if is_protected_path(target_path, protected_paths):
        if tmp_path.exists():
            try:
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
        raise PermissionError(
            f"Zielpfad '{target_path}' darf keine geschützte Konfigurations- oder Datenbankdatei überschreiben."
        )

    if not tmp_path.exists():
        raise FileNotFoundError(f"Temporäre Quelldatei nicht gefunden: {tmp_path}")

    size = tmp_path.stat().st_size
    if size < min_bytes:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise ValueError(f"Datei ist kleiner als Mindestgröße ({size} < {min_bytes} Bytes)")

    target_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Fsync temporary file descriptor before replacement if possible
        try:
            with open(tmp_path, "a+b") as f:
                f.flush()
                os.fsync(f.fileno())
        except (OSError, AttributeError):
            pass

        if target_path.exists():
            try:
                os.chmod(target_path, stat.S_IWRITE | stat.S_IREAD)
            except OSError:
                pass

        os.replace(tmp_path, target_path)
        return target_path
    finally:
        if tmp_path.exists():
            try:
                os.chmod(tmp_path, stat.S_IWRITE | stat.S_IREAD)
                tmp_path.unlink(missing_ok=True)
            except OSError:
                pass
