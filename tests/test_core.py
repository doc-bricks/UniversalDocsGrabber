"""Core tests for UniversalDocsGrabber."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest


def test_sanitize_filename_basic():
    from UniversalDocsGrabberV1 import sanitize_filename
    assert sanitize_filename("Hello World.pdf") == "Hello_World.pdf"
    assert "/" not in sanitize_filename("a/b/c.pdf")
    assert "\\" not in sanitize_filename("a\\b.pdf")


def test_sanitize_filename_none():
    from UniversalDocsGrabberV1 import sanitize_filename
    result = sanitize_filename(None)
    assert isinstance(result, str)
    assert len(result) > 0


def test_query_builder_generate_basic():
    """QueryBuilderDialog.generate() baut einen validen Gmail-Query-String."""
    import os
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    app = QApplication.instance() or QApplication(sys.argv)
    from UniversalDocsGrabberV1 import QueryBuilderDialog
    dlg = QueryBuilderDialog()
    # generate() schreibt Ergebnis ins interne QLineEdit; get_query() liest es aus
    dlg.generate()
    result = dlg.get_query()
    assert isinstance(result, str)
    # Default: rb_all aktiv + has:attachment -> mindestens diese Teile
    assert "has:attachment" in result


def test_search_profile_gmail_query_field():
    """SearchProfile speichert gmail_query korrekt."""
    from UniversalDocsGrabberV1 import SearchProfile
    import uuid
    p = SearchProfile(
        id=str(uuid.uuid4()),
        name="Test",
        group="",
        account_name="acc1"
    )
    assert hasattr(p, "gmail_query")
    assert p.gmail_query == ""
    d = p.to_dict()
    p2 = SearchProfile.from_dict(d)
    assert p2.gmail_query == ""
