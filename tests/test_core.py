"""Core tests for UniversalDocsGrabber."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))


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
    """QueryBuilderDialog.generate() builds a valid Gmail query string."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from UniversalDocsGrabberV1 import QueryBuilderDialog

    app = QApplication.instance() or QApplication(sys.argv)
    dlg = QueryBuilderDialog()
    dlg.generate()
    result = dlg.get_query()
    assert isinstance(result, str)
    assert "has:attachment" in result


def test_profile_dialog_formats_land_in_formats_field(monkeypatch):
    """ProfileDialog.get_profile() stores custom formats in DownloadSettings.formats."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from UniversalDocsGrabberV1 import DownloadSettings, MailAccount, ProfileDialog

    app = QApplication.instance() or QApplication(sys.argv)
    accounts = [MailAccount("acc1", "imap.example.org", "user@example.org")]
    dlg = ProfileDialog(accounts, global_settings=DownloadSettings())
    dlg.gb_over.setChecked(True)
    dlg.inp_fmt.setText("pdf, xls, csv")

    profile = dlg.get_profile()
    assert profile.override_settings is not None
    assert set(profile.override_settings.formats) == {"pdf", "xls", "csv"}
    assert isinstance(profile.override_settings.auto_categorize, bool)


def test_search_profile_gmail_query_field():
    """SearchProfile stores gmail_query correctly."""
    import uuid
    from UniversalDocsGrabberV1 import SearchProfile

    profile = SearchProfile(
        id=str(uuid.uuid4()),
        name="Test",
        group="",
        account_name="acc1",
    )
    assert hasattr(profile, "gmail_query")
    assert profile.gmail_query == ""
    restored = SearchProfile.from_dict(profile.to_dict())
    assert restored.gmail_query == ""


def test_profile_dialog_preserves_id_on_edit():
    """Editing a profile must preserve the original id."""
    import os

    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    from PySide6.QtWidgets import QApplication
    from UniversalDocsGrabberV1 import DownloadSettings, MailAccount, ProfileDialog, SearchProfile

    app = QApplication.instance() or QApplication(sys.argv)
    original = SearchProfile("stable-id-42", "Orig", "G", "acc1")
    accounts = [MailAccount("acc1", "imap.example.org", "user@example.org")]
    dlg = ProfileDialog(accounts, profile=original, global_settings=DownloadSettings())
    edited = dlg.get_profile()
    assert edited.id == "stable-id-42"


def test_converter_returns_false_when_ocr_unavailable(tmp_path, monkeypatch):
    """convert_img and convert_txt must fail cleanly without OCR helpers."""
    import UniversalDocsGrabberV1 as app

    monkeypatch.setattr(app, "OCR_AVAILABLE", False)
    log_calls = []
    conv = app.UniversalConverter(log_calls.append)

    dummy = tmp_path / "dummy.png"
    dummy.write_bytes(b"fake")
    result_img = conv.convert_img(str(dummy), str(tmp_path / "out.pdf"))
    assert result_img is False
    assert any("fehlt" in msg or "verf" in msg for msg in log_calls)

    log_calls.clear()
    txt_file = tmp_path / "dummy.txt"
    txt_file.write_text("hello", encoding="utf-8")
    result_txt = conv.convert_txt(str(txt_file), str(tmp_path / "out2.pdf"))
    assert result_txt is False
    assert any("fehlt" in msg or "verf" in msg for msg in log_calls)


def test_connect_imap_passes_timeout(monkeypatch):
    """connect_imap must pass timeout=30 to IMAP4_SSL to prevent indefinite hangs."""
    import UniversalDocsGrabberV1 as app

    captured = {}

    class FakeIMAP:
        def __init__(self, host, port, timeout=None):
            captured["timeout"] = timeout
        def login(self, user, pwd):
            pass
        def select(self, folder, readonly=False):
            return "OK", []

    monkeypatch.setattr(app.imaplib, "IMAP4_SSL", FakeIMAP)
    monkeypatch.setattr(app, "KEYRING_AVAIL", True)
    monkeypatch.setattr(app.keyring, "get_password", lambda *_: "secret")

    worker = app.GrabberWorker([], [], app.DownloadSettings(), None, [])
    worker.accounts = {"test": app.MailAccount("test", "imap.example.org", "user@example.org")}
    worker.connect_imap("test")

    assert captured.get("timeout") == 30


def test_ocr_temp_file_cleaned_up_on_exception(tmp_path, monkeypatch):
    """add_text_layer muss .temp.pdf löschen wenn shutil.move nach dem Schreiben wirft."""
    import UniversalDocsGrabberV1 as app

    src = tmp_path / "doc.pdf"
    src.write_bytes(b"%PDF-fake")
    tmp_file = src.with_suffix(".temp.pdf")

    log_calls = []
    ocr = app.OCRProcessor(log_calls.append)

    monkeypatch.setattr(app, "OCR_AVAILABLE", True)

    fake_page = object()

    class FakePdfReader:
        def __init__(self, _):
            self.pages = [fake_page]

    class FakePdfWriter:
        def add_page(self, page):
            pass
        def write(self, f):
            f.write(b"%PDF-fake-written")

    def fake_convert_from_path(*a, **kw):
        return ["img"]

    def fake_image_to_pdf(*a, **kw):
        return b"%PDF-1.4"

    def fake_move(src_path, dst_path):
        raise OSError("move failed")

    monkeypatch.setattr(app, "convert_from_path", fake_convert_from_path)
    monkeypatch.setattr(app.pytesseract, "image_to_pdf_or_hocr", fake_image_to_pdf)
    monkeypatch.setattr(app, "PdfReader", FakePdfReader)
    monkeypatch.setattr(app, "PdfWriter", FakePdfWriter)
    monkeypatch.setattr(app.shutil, "move", fake_move)

    result, _ = ocr.add_text_layer(src)

    assert result is False
    assert not tmp_file.exists(), "Temp-Datei wurde nicht aufgeräumt"


def test_convert_word_uses_docx2pdf_fallback_without_win32(tmp_path, monkeypatch):
    """The docx2pdf fallback must stay reachable without win32com."""
    import UniversalDocsGrabberV1 as app

    dummy_docx = tmp_path / "dummy.docx"
    dummy_docx.write_text("hello", encoding="utf-8")
    out_pdf = tmp_path / "dummy.pdf"
    log_calls = []
    conv = app.UniversalConverter(log_calls.append)

    monkeypatch.setattr(app, "WIN32_AVAILABLE", False)
    monkeypatch.setattr(app, "DOCX2PDF_AVAILABLE", True)

    def fake_docx2pdf_convert(input_path, output_path):
        Path(output_path).write_text(f"converted:{Path(input_path).name}", encoding="utf-8")

    monkeypatch.setattr(app, "docx2pdf_convert", fake_docx2pdf_convert)

    result = conv.convert_word(str(dummy_docx), str(out_pdf))

    assert result is True
    assert out_pdf.exists()
    assert out_pdf.read_text(encoding="utf-8") == "converted:dummy.docx"
    assert not any("Word-Konverter" in msg for msg in log_calls)
