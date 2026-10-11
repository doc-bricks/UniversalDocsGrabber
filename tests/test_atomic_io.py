# -*- coding: utf-8 -*-
"""
Contract and regression test suite for atomic I/O, durability, and protected paths in UniversalDocsGrabber.
"""

import json
import os
import stat
from pathlib import Path

import pytest

from atomic_io import (
    atomic_publish_file,
    atomic_write_bytes,
    atomic_write_json,
    atomic_write_text,
    get_default_protected_paths,
    is_protected_path,
    resolve_path,
)
from cli import export_documents_to_csv
from UniversalDocsGrabberV1 import (
    CONFIG_FILE,
    DOCS_DB,
    write_library_export,
)


def test_resolve_path():
    p = resolve_path("~")
    assert p.is_absolute()
    assert str(p) != "~"


def test_atomic_write_text(tmp_path: Path):
    target = tmp_path / "subdir" / "test.txt"
    written = atomic_write_text(target, "Grüße mit Umlauten äöüß\n")
    assert written == target.resolve()
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "Grüße mit Umlauten äöüß\n"


def test_atomic_write_json(tmp_path: Path):
    target = tmp_path / "data.json"
    data = {"app": "UniversalDocsGrabber", "version": "1.1.7", "count": 42}
    written = atomic_write_json(target, data, indent=2)
    assert written == target.resolve()
    assert target.exists()
    loaded = json.loads(target.read_text(encoding="utf-8"))
    assert loaded == data


def test_atomic_write_bytes(tmp_path: Path):
    target = tmp_path / "binary.bin"
    payload = b"\x00\x01\x02\x03\xff\xfe"
    written = atomic_write_bytes(target, payload, min_bytes=4)
    assert written == target.resolve()
    assert target.read_bytes() == payload


def test_atomic_write_bytes_rejects_insufficient_length(tmp_path: Path):
    target = tmp_path / "short.bin"
    with pytest.raises(ValueError, match="Binärdaten sind unvollständig"):
        atomic_write_bytes(target, b"12", min_bytes=10)
    assert not target.exists()


def test_is_protected_path_matching(tmp_path: Path):
    config_file = tmp_path / "config_v1.json"
    config_file.touch()
    docs_db = tmp_path / "documents.json"
    docs_db.touch()
    protected = {config_file, docs_db}

    assert is_protected_path(config_file, protected)
    assert is_protected_path(str(config_file), protected)
    assert is_protected_path(docs_db, protected)
    assert not is_protected_path(tmp_path / "other.json", protected)


def test_atomic_write_rejects_protected_path(tmp_path: Path):
    config_file = tmp_path / "config_v1.json"
    config_file.write_text("original content", encoding="utf-8")
    protected = {config_file}

    with pytest.raises(PermissionError, match="geschützte Konfigurations- oder Datenbankdatei"):
        atomic_write_text(config_file, "overwrite attempt", protected_paths=protected)

    assert config_file.read_text(encoding="utf-8") == "original content"

    with pytest.raises(PermissionError, match="geschützte Konfigurations- oder Datenbankdatei"):
        atomic_write_json(config_file, {"evil": True}, protected_paths=protected)

    assert config_file.read_text(encoding="utf-8") == "original content"

    with pytest.raises(PermissionError, match="geschützte Konfigurations- oder Datenbankdatei"):
        atomic_write_bytes(config_file, b"evil", protected_paths=protected)

    assert config_file.read_text(encoding="utf-8") == "original content"


def test_atomic_write_preserves_original_on_serialization_failure(tmp_path: Path):
    target = tmp_path / "original.json"
    target.write_text("valid json", encoding="utf-8")

    class UnserializableObject:
        pass

    with pytest.raises(TypeError):
        atomic_write_json(target, {"bad": UnserializableObject()})

    # File on disk remains untouched
    assert target.read_text(encoding="utf-8") == "valid json"


def test_atomic_write_handles_readonly_target(tmp_path: Path):
    target = tmp_path / "readonly.txt"
    target.write_text("v1", encoding="utf-8")
    # Make target read-only
    os.chmod(target, stat.S_IREAD)

    try:
        atomic_write_text(target, "v2 updated")
        assert target.read_text(encoding="utf-8") == "v2 updated"
    finally:
        os.chmod(target, stat.S_IWRITE | stat.S_IREAD)


def test_atomic_publish_file_success(tmp_path: Path):
    tmp_source = tmp_path / "source.tmp"
    tmp_source.write_text("temporary export data", encoding="utf-8")
    target = tmp_path / "published.txt"

    atomic_publish_file(tmp_source, target, min_bytes=5)
    assert not tmp_source.exists()
    assert target.exists()
    assert target.read_text(encoding="utf-8") == "temporary export data"


def test_atomic_publish_file_rejects_protected(tmp_path: Path):
    protected_file = tmp_path / "config_v1.json"
    protected_file.write_text("safe config", encoding="utf-8")

    tmp_source = tmp_path / "export.tmp"
    tmp_source.write_text("illegal export", encoding="utf-8")

    with pytest.raises(PermissionError, match="geschützte Konfigurations- oder Datenbankdatei"):
        atomic_publish_file(tmp_source, protected_file, protected_paths={protected_file})

    assert protected_file.read_text(encoding="utf-8") == "safe config"
    assert not tmp_source.exists()


def test_write_library_export_atomic_and_protected(tmp_path: Path, monkeypatch):
    protected_db = tmp_path / "documents.json"
    protected_db.write_text("[]", encoding="utf-8")
    monkeypatch.setattr("UniversalDocsGrabberV1.get_default_protected_paths", lambda: {protected_db})

    # Normal export works
    export_target = tmp_path / "export.json"
    payload = {"schema": "docsgrabber-library", "profiles": []}
    write_library_export(export_target, payload)
    assert export_target.exists()
    loaded = json.loads(export_target.read_text(encoding="utf-8"))
    assert loaded["schema"] == "docsgrabber-library"

    # Export to protected target is rejected
    with pytest.raises(PermissionError):
        write_library_export(protected_db, payload)
    assert protected_db.read_text(encoding="utf-8") == "[]"


def test_export_documents_to_csv_atomic_and_protected(tmp_path: Path, monkeypatch):
    protected_cfg = tmp_path / "config_v1.json"
    protected_cfg.write_text("{}", encoding="utf-8")
    monkeypatch.setattr("cli.get_default_protected_paths", lambda: {protected_cfg})

    docs = [
        {
            "date": "2026-10-11",
            "profile": "Rechnungen",
            "filename": "Rechnung_1.pdf",
            "path": str(tmp_path / "Rechnung_1.pdf"),
            "sender": "provider@example.com",
            "subject": "Rechnung Oktober",
        }
    ]

    # Valid export
    csv_target = tmp_path / "export.csv"
    count = export_documents_to_csv(docs, csv_target)
    assert count == 1
    assert csv_target.exists()
    content = csv_target.read_text(encoding="utf-8-sig")
    assert "Rechnung Oktober" in content
    assert "Rechnungen" in content

    # Rejection of protected file
    with pytest.raises(PermissionError):
        export_documents_to_csv(docs, protected_cfg)
    assert protected_cfg.read_text(encoding="utf-8") == "{}"


def test_get_default_protected_paths(tmp_path: Path):
    protected = get_default_protected_paths(tmp_path)
    assert resolve_path(tmp_path / "config_v1.json") in protected
    assert resolve_path(tmp_path / "documents.json") in protected
    assert resolve_path(tmp_path / "token.json") in protected
    # Verify that global defaults resolve paths correctly
    global_protected = get_default_protected_paths()
    assert resolve_path(CONFIG_FILE) in global_protected or resolve_path(DOCS_DB) in global_protected
