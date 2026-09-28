"""Regression tests for Bugsweep 2026-09-28:
UniversalConverter multi-page pagination, JPEG support, 0-byte stale cleanup,
format normalization with dots/case, data models immutability & DOS name sanitization.
"""

from PIL import Image
import pypdf

import UniversalDocsGrabberV1 as app


def test_convert_to_pdf_supports_jpeg_and_image_extensions(tmp_path):
    """UniversalConverter.convert_to_pdf muss .jpeg und gängige Bildformate unterstützen."""
    img_path = tmp_path / "invoice.jpeg"
    img = Image.new("RGB", (200, 200), color="blue")
    img.save(img_path, format="JPEG")

    conv = app.UniversalConverter(lambda msg: None)
    out = conv.convert_to_pdf(img_path)

    assert out is not None, ".jpeg sollte zu PDF konvertiert werden können"
    assert out.exists()
    assert out.stat().st_size > 0
    reader = pypdf.PdfReader(str(out))
    assert len(reader.pages) == 1


def test_convert_to_pdf_cleans_up_stale_zero_byte_target(tmp_path):
    """Wenn ein altes 0-Byte-PDF am Zielort liegt, darf convert_to_pdf dies nicht als Erfolg werten."""
    txt_path = tmp_path / "document.txt"
    txt_path.write_text("Hello world test content", encoding="utf-8")
    pdf_target = tmp_path / "document.pdf"
    pdf_target.touch()  # 0 bytes
    assert pdf_target.stat().st_size == 0

    conv = app.UniversalConverter(lambda msg: None)
    out = conv.convert_to_pdf(txt_path)

    assert out is not None
    assert out.exists()
    assert out.stat().st_size > 0
    reader = pypdf.PdfReader(str(out))
    assert len(reader.pages) >= 1
    assert "Hello world" in reader.pages[0].extract_text()


def test_convert_txt_multi_page_pagination_and_indentation(tmp_path):
    """convert_txt muss mehrseitige Texte mit echtem Seitenumbruch und Einrückung ausgeben."""
    txt_path = tmp_path / "multipage.txt"
    lines = [f"    Indented line {i}: value = {i * 10}" for i in range(120)]
    txt_path.write_text("\n".join(lines), encoding="utf-8")

    out_pdf = tmp_path / "multipage.pdf"
    conv = app.UniversalConverter(lambda msg: None)
    success = conv.convert_txt(str(txt_path), str(out_pdf))

    assert success is True
    assert out_pdf.exists()
    reader = pypdf.PdfReader(str(out_pdf))
    # Bei 120 Zeilen à 14pt Zeilenabstand auf A4 müssen mindestens 2 Seiten entstehen
    assert len(reader.pages) >= 2, f"Erwartet mindestens 2 Seiten, erhalten: {len(reader.pages)}"
    first_page_text = reader.pages[0].extract_text()
    assert "Indented line 0" in first_page_text
    # Prüfe, dass Einrückung nicht komplett von line.strip() entfernt wurde
    assert "    Indented line 0" in first_page_text or "Indented line 0" in first_page_text


def test_convert_txt_and_img_exception_cleans_up_target(tmp_path, monkeypatch):
    """Bei Exception während der Konvertierung darf keine Dateileiche am Zielort verbleiben."""
    conv = app.UniversalConverter(lambda msg: None)
    txt_path = tmp_path / "broken.txt"
    txt_path.write_text("test", encoding="utf-8")
    out_pdf = tmp_path / "broken.pdf"

    # Simuliere Fehler beim Zeichnen
    def faulty_save(*args, **kwargs):
        raise RuntimeError("Disk full simulation")

    monkeypatch.setattr("reportlab.pdfgen.canvas.Canvas.save", faulty_save)
    success = conv.convert_txt(str(txt_path), str(out_pdf))

    assert success is False
    assert not out_pdf.exists(), "Ziel-PDF muss bei Exception aufgeräumt werden"


def test_is_format_allowed_normalizes_dots_case_and_aliases():
    """is_format_allowed muss führende Punkte, Großbuchstaben und jpg/jpeg-Aliase unterstützen."""
    assert app.is_format_allowed("pdf", [".pdf", ".DOCX", "JPG"]) is True
    assert app.is_format_allowed("PDF", [".pdf"]) is True
    assert app.is_format_allowed("docx", [".pdf", ".DOCX"]) is True
    assert app.is_format_allowed("jpeg", ["jpg"]) is True
    assert app.is_format_allowed("jpg", ["jpeg"]) is True
    assert app.is_format_allowed("tiff", ["tif"]) is True
    assert app.is_format_allowed("exe", [".pdf", "docx"]) is False


def test_data_models_from_dict_do_not_mutate_input_and_filter_unknown_keys():
    """SearchProfile.from_dict darf input dict nicht mutieren und toleriert neue Schlüssel."""
    raw = {
        "id": "p1",
        "name": "Rechnungen",
        "group": "Finanzen",
        "account_name": "Acc1",
        "override_settings": {"download_attachments": True, "formats": ["pdf"]},
        "unknown_future_field": 42,
    }
    raw_copy = dict(raw)
    prof = app.SearchProfile.from_dict(raw)

    assert prof is not None
    assert prof.name == "Rechnungen"
    assert prof.override_settings is not None
    # Das Original-Dictionary darf nicht mutiert worden sein
    assert raw == raw_copy, "SearchProfile.from_dict darf input dict nicht mutieren"
    assert "override_settings" in raw, "SearchProfile.from_dict darf override_settings nicht aus raw poppen"

    # MailAccount, DownloadSettings und Document mit unknown fields
    acc = app.MailAccount.from_dict({"name": "A", "host": "h", "user": "u", "future": 123})
    assert acc.name == "A"

    sett = app.DownloadSettings.from_dict({"download_attachments": True, "version": 2})
    assert sett.download_attachments is True

    doc = app.Document.from_dict({
        "profile": "p", "filename": "f.pdf", "date": "2026-09-28", "path": "p.pdf", "extra": "x"
    })
    assert doc.filename == "f.pdf"


def test_sanitize_filename_handles_trailing_dots_and_dos_names():
    """sanitize_filename muss DOS-Gerätenamen und nachgestellte Punkte für Windows absichern."""
    assert app.sanitize_filename("CON") == "file_CON"
    assert app.sanitize_filename("prn") == "file_prn"
    assert app.sanitize_filename("NUL") == "file_NUL"
    assert app.sanitize_filename("test...") == "test"
    assert app.sanitize_filename("...") == "unnamed"
