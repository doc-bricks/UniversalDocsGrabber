import sys
import json
import os
import time
import logging
import re
import io
import shutil
import hashlib
import imaplib
import email
import email.header
from pathlib import Path
from dataclasses import dataclass, asdict, field
from datetime import datetime, date, timedelta
from typing import List, Optional

# GUI Imports
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QHBoxLayout, QLabel, QPushButton, QTableWidget,
                             QTableWidgetItem, QHeaderView, QMessageBox, QDialog,
                             QFormLayout, QComboBox, QGroupBox, QCheckBox,
                             QTabWidget, QDialogButtonBox, QTreeWidget, QTreeWidgetItem,
                             QLineEdit, QFileDialog, QPlainTextEdit, QAbstractItemView,
                             QDateEdit, QRadioButton, QGridLayout, QSpinBox)
from PySide6.QtCore import Qt, QThread, Signal, QUrl, QDate, QTimer
from PySide6.QtGui import QColor, QPalette, QDesktopServices

# PDF / OCR / Conversion
try:
    from xhtml2pdf import pisa
    PISA_AVAILABLE = True
except ImportError:
    pisa = None  # Sentinel für monkeypatch in Tests
    PISA_AVAILABLE = False

try:
    import pytesseract
    from pdf2image import convert_from_path
    from pypdf import PdfReader, PdfWriter
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib.utils import ImageReader
    from PIL import Image
    OCR_AVAILABLE = True
except ImportError:
    import types as _types
    pytesseract = _types.SimpleNamespace(image_to_pdf_or_hocr=None)  # Sentinel: via monkeypatch setzbar
    convert_from_path = None
    PdfReader = None
    PdfWriter = None
    OCR_AVAILABLE = False

try:
    import win32com.client
    import pythoncom
    WIN32_AVAILABLE = True
except ImportError:
    win32com = None
    pythoncom = None
    WIN32_AVAILABLE = False

try:
    from docx2pdf import convert as docx2pdf_convert
    DOCX2PDF_AVAILABLE = True
except ImportError:
    docx2pdf_convert = None
    DOCX2PDF_AVAILABLE = False

try:
    from app_icon_loader import get_app_icon, load_app_icon
except ImportError:
    def get_app_icon():
        return None

    def load_app_icon():
        return None

# Security
try:
    import keyring
    KEYRING_AVAIL = True
except ImportError:
    KEYRING_AVAIL = False

# ==================== CONFIG ====================

APP_NAME = "UniversalDocsGrabber_V1"
APP_VERSION = "1.x"
EXPORT_SCHEMA = "docsgrabber-library"
EXPORT_SCHEMA_VERSION = "1.0"

# ==================== CONSTANTS ====================

# Log messages (static, no variables)
LOG_MSG_WORD_UNAVAILABLE = "Word-Konverter nicht verfügbar (win32com/docx2pdf fehlt)"
LOG_MSG_OCR_UNAVAILABLE = "OCR nicht verfügbar (pytesseract/pdf2image fehlt)"
LOG_MSG_NO_MAILS = "   (Keine Mails)"
LOG_MSG_OCR_PROCESSING = "   ⚙️ OCR..."
LOG_MSG_DEDUP_START = "🧹 Starte Hash-Checker..."

# UI strings
UI_TITLE_ACCOUNT_DIALOG = "IMAP Account"
UI_TITLE_PROFILE_DIALOG = "Suchprofil (IMAP)"
UI_LABEL_BASIS = "Basis"
UI_LABEL_TIME_FILTER = "Zeit-Filter"
UI_LABEL_GLOBAL = "Global"
UI_LABEL_SETTINGS_OVERRIDE = "Settings Override"
UI_BTN_START = "🚀 START"
UI_BTN_RUNNING = "⏳ Läuft..."
UI_TAB_ACCOUNTS = "🔑 Konten"
UI_TAB_DOCS = "📂 Dokumente"
UI_TAB_SETTINGS = "⚙️ Einstellungen"
UI_TAB_LOG = "📝 Protokoll"
UI_BTN_ADD_PROFILE = "➕ Profil"
UI_BTN_DELETE_PROFILE = "❌ Profil löschen"
UI_BTN_ADD_ACCOUNT = "➕ Account"
UI_BTN_DELETE_ACCOUNT = "❌ Account löschen"
UI_BTN_BROWSE_PATH = "Ordner wählen..."
UI_WARN_NO_ACCOUNT_TITLE = "Fehler"
UI_WARN_NO_ACCOUNT_MSG = "Zuerst Account anlegen!"
DEFAULT_GROUP = "Allgemein"  # Default group name for uncategorized profiles
UI_EXPORT_LABEL = "Companion-Export"
UI_BTN_EXPORT_LIBRARY = "Redigierten Export speichern..."
UI_EXPORT_SUCCESS_TITLE = "Export gespeichert"
UI_EXPORT_ERROR_TITLE = "Export fehlgeschlagen"
UI_SCHEDULER_LABEL = "⏰ Scheduler"
UI_SCHEDULER_ACTIVE = "Scheduler aktiv: alle {interval} Min."
UI_SCHEDULER_INACTIVE = "Scheduler inaktiv"
UI_SCHEDULER_NEXT = "Nächster Scan: {time}"
SCHEDULER_INTERVALS = [0, 15, 30, 60, 120, 360, 720, 1440]  # 0=aus, dann Minuten
SCHEDULER_LABELS = ["Aus", "15 Min.", "30 Min.", "1 Stunde", "2 Stunden", "6 Stunden", "12 Stunden", "24 Stunden"]
BASE_DIR = Path.home() / ".univ_docs_grabber"
BASE_DIR.mkdir(parents=True, exist_ok=True)
CONFIG_FILE = BASE_DIR / "config_v1.json"
DOCS_DB = BASE_DIR / "documents.json"

# Poppler Pfad für PDF-zu-Bild-Konvertierung (OCR)
# Falls poppler nicht im PATH: Pfad hier setzen (z.B. "C:\\Program Files\\poppler\\Library\\bin")
POPPLER_PATH = None  # None = Auto-Detect aus PATH

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger(APP_NAME)

# ==================== DATA MODELS ====================

@dataclass
class MailAccount:
    """IMAP E-Mail Account Konfiguration.

    Attributes:
        name: Eindeutiger Account-Name
        host: IMAP Server (z.B. imap.gmx.net)
        user: E-Mail-Adresse / Username
        port: IMAP Port (Standard: 993)
        search_folder: IMAP Ordner für Suche (Standard: INBOX)
    """
    name: str
    host: str
    user: str
    port: int = 993
    search_folder: str = "INBOX"  # Standardordner für Suche

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@dataclass
class DownloadSettings:
    """Download- und Konvertierungseinstellungen.

    Attributes:
        download_attachments: Anhänge herunterladen
        convert_body_to_pdf: E-Mail Body als PDF speichern
        keep_html: HTML-Dateien behalten (nicht implementiert)
        convert_all_to_pdf: Alle Formate zu PDF konvertieren
        keep_original_after_convert: Originaldatei nach Konvertierung behalten
        enable_hash_check: Duplikate-Erkennung aktivieren
        formats: Erlaubte Datei-Formate
    """
    download_attachments: bool = True
    convert_body_to_pdf: bool = True
    keep_html: bool = False
    convert_all_to_pdf: bool = False
    keep_original_after_convert: bool = False
    enable_hash_check: bool = False
    auto_categorize: bool = False
    category_rules: List[dict] = field(default_factory=list)
    formats: List[str] = field(default_factory=lambda: ["pdf", "docx", "doc", "jpg", "png"])

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)

@dataclass
class SearchProfile:
    """IMAP-Suchprofil mit Filtern.

    Attributes:
        id: Eindeutige Profil-ID (Timestamp)
        name: Anzeigename des Profils
        group: Gruppen-Kategorie (für Organisation)
        account_name: Welcher MailAccount verwendet wird
        query_subject: Filter nach Betreff (optional)
        query_sender: Filter nach Absender (optional)
        query_since: Filter ab Datum YYYY-MM-DD (optional)
        target_folder: Zielordner-Name (falls abweichend von Profilname)
        active: Profil aktiv/inaktiv
        override_settings: Profil-spezifische Download-Einstellungen
    """
    id: str
    name: str
    group: str
    account_name: str  # Welcher Account genutzt wird
    query_subject: str = ""
    query_sender: str = ""
    query_since: str = ""  # Datum YYYY-MM-DD
    target_folder: str = ""
    active: bool = True
    override_settings: Optional[DownloadSettings] = None
    gmail_query: str = ""  # Freitext-Query (gespeichert, nicht für IMAP-Worker)

    def to_dict(self):
        d = asdict(self)
        if self.override_settings:
            d['override_settings'] = self.override_settings.to_dict()
        return d

    @classmethod
    def from_dict(cls, d):
        over = d.pop('override_settings', None)
        # Rückwärtskompatibilität: Ältere Configs ohne gmail_query
        d.setdefault('gmail_query', '')
        obj = cls(**d)
        if over:
            obj.override_settings = DownloadSettings.from_dict(over)
        return obj

@dataclass
class Document:
    """Heruntergeladenes Dokument (Datenbank-Entry).

    Attributes:
        profile: Name des Suchprofils
        filename: Dateiname auf Disk
        date: Download-Datum (YYYY-MM-DD)
        path: Vollständiger Pfad zur Datei
        sender: E-Mail Absender
        subject: E-Mail Betreff
    """
    profile: str
    filename: str
    date: str
    path: str
    sender: str = ""
    subject: str = ""

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, d):
        return cls(**d)


def build_account_ref(account_name: str) -> str:
    """Erzeugt eine stabile, redigierte Referenz für einen Mail-Account."""
    normalized = (account_name or "").strip().encode("utf-8")
    digest = hashlib.sha256(normalized).hexdigest()[:12]
    return f"account-{digest}" if digest else "account-unknown"


def redact_path_hint(path_value: str, base_path: Path) -> dict:
    """Redigiert absolute Pfade auf relative Hinweise oder den Dateinamen."""
    path = Path(path_value)
    try:
        rel_path = path.resolve(strict=False).relative_to(base_path.resolve(strict=False))
        return {"kind": "relative", "value": rel_path.as_posix()}
    except ValueError:
        return {"kind": "basename", "value": path.name}


def infer_document_category(path_value: str, base_path: Path, profile_name: str, target_folder: str = "") -> str:
    """Leitet optional eine Kategorie aus dem Dokumentpfad ab.

    Kategorien liegen als Unterordner innerhalb des Profil- bzw. Zielordners.
    Liegt ein Dokument direkt im Profil-/Zielordner (len(parts) < 2), existiert keine
    Kategorie (Rückgabe: leerer String).
    """
    profile_folder = sanitize_filename(profile_name)
    target_folder_sanitized = sanitize_filename(target_folder) if target_folder else ""
    path = Path(path_value)
    try:
        rel_path = path.resolve(strict=False).relative_to(base_path.resolve(strict=False))
    except ValueError:
        return ""

    parts = list(rel_path.parts[:-1])
    # Mindestens 2 Ebenen unter base_path erforderlich: <profile_or_target_folder>/<category_folder>/.../<file>
    if len(parts) < 2:
        return ""
    if parts[0] == profile_folder or (target_folder_sanitized and parts[0] == target_folder_sanitized):
        return parts[1]
    return ""


def collect_category_entries(
    global_settings: DownloadSettings,
    profiles: List[SearchProfile],
    documents: List[Document],
    base_path: Path,
) -> List[dict]:
    """Sammelt Kategorien aus Regeln und vorhandenen Dokumentpfaden."""
    category_map = {}
    profile_target_map = {profile.name: profile.target_folder for profile in profiles}

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

    for rule in global_settings.category_rules or []:
        add_category(rule.get("folder", ""), "global_rule")

    for profile in profiles:
        settings = profile.override_settings if profile.override_settings else global_settings
        for rule in settings.category_rules or []:
            add_category(rule.get("folder", ""), "profile_rule", profile.name)

    for document in documents:
        target_folder = profile_target_map.get(document.profile, "")
        add_category(
            infer_document_category(document.path, base_path, document.profile, target_folder),
            "document_path",
            document.profile,
        )

    return [
        {
            "name": name,
            "sources": sorted(entry["sources"]),
            "profile_names": sorted(entry["profile_names"]),
        }
        for name, entry in sorted(category_map.items())
    ]


def build_library_export_payload(
    profiles: List[SearchProfile],
    accounts: List[MailAccount],
    documents: List[Document],
    global_settings: DownloadSettings,
    base_path: Path,
    scheduler_interval: int = 0,
    exported_at: Optional[datetime] = None,
) -> dict:
    """Baut den redigierten Export für Web/PWA-Companions."""
    export_dt = exported_at or datetime.now().astimezone()
    export_timestamp = export_dt.isoformat(timespec="seconds")
    account_refs = {account.name: build_account_ref(account.name) for account in accounts}
    profile_target_map = {profile.name: profile.target_folder for profile in profiles}

    documents_by_profile = {}
    exported_documents = []
    for document in documents:
        doc_path = Path(document.path)
        exists = doc_path.exists()
        target_folder = profile_target_map.get(document.profile, "")
        category = infer_document_category(document.path, base_path, document.profile, target_folder)
        exported_doc = {
            "profile_name": document.profile,
            "filename": document.filename,
            "document_date": document.date,
            "file_type": doc_path.suffix.lower().lstrip("."),
            "category": category or None,
            "path_hint": redact_path_hint(document.path, base_path),
            "status": "available" if exists else "missing",
            "sha256": calculate_file_hash(doc_path) if exists else None,
        }
        exported_documents.append(exported_doc)
        documents_by_profile.setdefault(document.profile, []).append(exported_doc)

    exported_profiles = []
    profile_stats = []
    for profile in profiles:
        effective_settings = profile.override_settings if profile.override_settings else global_settings
        profile_docs = documents_by_profile.get(profile.name, [])
        last_document_date = max((doc["document_date"] for doc in profile_docs), default=None)
        exported_profiles.append(
            {
                "id": profile.id,
                "name": profile.name,
                "group": profile.group or DEFAULT_GROUP,
                "active": profile.active,
                "account_ref": account_refs.get(profile.account_name, build_account_ref(profile.account_name)),
                "target_folder": profile.target_folder,
                "filters": {
                    "subject": profile.query_subject,
                    "sender": profile.query_sender,
                    "since": profile.query_since,
                    "gmail_query": profile.gmail_query,
                },
                "effective_settings": {
                    "download_attachments": effective_settings.download_attachments,
                    "convert_body_to_pdf": effective_settings.convert_body_to_pdf,
                    "convert_all_to_pdf": effective_settings.convert_all_to_pdf,
                    "enable_hash_check": effective_settings.enable_hash_check,
                    "auto_categorize": effective_settings.auto_categorize,
                    "category_rule_count": len(effective_settings.category_rules or []),
                    "formats": list(effective_settings.formats or []),
                },
                "document_count": len(profile_docs),
                "last_document_date": last_document_date,
            }
        )
        profile_stats.append(
            {
                "profile_name": profile.name,
                "document_count": len(profile_docs),
                "last_document_date": last_document_date,
                "active": profile.active,
            }
        )

    exported_accounts = [
        {
            "ref": account_refs.get(account.name, build_account_ref(account.name)),
            "profile_count": sum(1 for profile in profiles if profile.account_name == account.name),
        }
        for account in accounts
    ]

    categories = collect_category_entries(global_settings, profiles, documents, base_path)

    return {
        "schema": EXPORT_SCHEMA,
        "schema_version": EXPORT_SCHEMA_VERSION,
        "app": {
            "name": APP_NAME,
            "version": APP_VERSION,
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
            "active_profile_count": sum(1 for profile in profiles if profile.active),
            "exported_document_count": len(exported_documents),
            "scheduler_interval_minutes": scheduler_interval,
            "profile_stats": profile_stats,
        },
    }


def write_library_export(path: Path, payload: dict) -> None:
    """Schreibt den redigierten Bibliotheksexport als UTF-8 JSON ohne BOM."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

# ==================== HELPERS ====================

def sanitize_filename(name: str) -> str:
    """Bereinigt Dateinamen von ungültigen Zeichen und limitiert Länge.

    Args:
        name: Roher Dateiname

    Returns:
        Bereinigte Dateiname (max 100 Zeichen)
    """
    if not name or not isinstance(name, str):
        return "unnamed"
    s = re.sub(r'[^\w\s\.-]', '', name)
    s = re.sub(r'\s+', '_', s)
    result = s.strip()[:100]
    return result if result else "unnamed"

def calculate_file_hash(path: Path) -> Optional[str]:
    """Berechnet SHA-256 Hash einer Datei.

    Args:
        path: Pfad zur Datei

    Returns:
        SHA-256 Hash als Hex-String oder None bei Fehler
    """
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                h.update(chunk)
        return h.hexdigest()
    except (FileNotFoundError, PermissionError, OSError) as e:
        logger.warning(f"Hash calculation failed for {path}: {e}")
        return None


def safe_decode_payload(payload: Optional[bytes], charset: Optional[str] = None) -> str:
    """Dekodiert E-Mail-Payload-Bytes robust mit Fallback bei unbekannten/ungültigen Charsets.

    Args:
        payload: Rohe Bytes des Payloads
        charset: Deklarierter Charset-Name (kann ungültig oder unbekannt sein)

    Returns:
        Dekodierter String
    """
    if payload is None:
        return ""
    if charset:
        try:
            return payload.decode(charset, errors='ignore')
        except (LookupError, UnicodeDecodeError):
            pass
    try:
        return payload.decode('utf-8', errors='ignore')
    except (LookupError, UnicodeDecodeError):
        return payload.decode('latin-1', errors='ignore')


def decode_header_str(header_val: Optional[str]) -> str:
    """Dekodiert E-Mail Header mit verschiedenen Encodings.

    Args:
        header_val: Roher Header-Wert

    Returns:
        Dekodierter String oder "Unknown" bei leerem Input
    """
    if not header_val:
        return "Unknown"
    try:
        decoded_list = email.header.decode_header(header_val)
        val = ""
        for text, encoding in decoded_list:
            if isinstance(text, bytes):
                if encoding:
                    val += text.decode(encoding, errors='ignore')
                else:
                    val += text.decode('utf-8', errors='ignore')
            else:
                val += str(text)
        return val
    except (UnicodeDecodeError, LookupError, AttributeError, ValueError) as e:
        logger.warning(f"Header decode failed: {e}")
        return str(header_val)

# ==================== CONVERTER & OCR ====================

class UniversalConverter:
    def __init__(self, log_func): self.log = log_func
    def convert_to_pdf(self, input_path: Path) -> Optional[Path]:
        input_path = Path(input_path); ext = input_path.suffix.lower(); output_path = input_path.with_suffix(".pdf")
        if output_path.exists(): return output_path
        success = False
        if ext in [".docx", ".doc", ".rtf"]: success = self.convert_word(str(input_path), str(output_path))
        elif ext == ".txt": success = self.convert_txt(str(input_path), str(output_path))
        elif ext in [".jpg", ".png", ".bmp"]: success = self.convert_img(str(input_path), str(output_path))
        return output_path if success else None

    def convert_word(self, i, o):
        if not WIN32_AVAILABLE and not DOCX2PDF_AVAILABLE:
            self.log(LOG_MSG_WORD_UNAVAILABLE)
            return False
        if WIN32_AVAILABLE:
            try:
                pythoncom.CoInitialize()
            except (OSError, RuntimeError):
                pass  # CoInitialize kann schon erfolgt sein
            word = None
            doc = None
            try:
                word = win32com.client.Dispatch("Word.Application")
                word.Visible = False
                doc = word.Documents.Open(i)
                doc.ExportAsFixedFormat(o, 17)
                return True
            except Exception as e:
                self.log(f"Word-Konvertierung fehlgeschlagen: {e}")
            finally:
                if doc is not None:
                    try:
                        doc.Close(False)
                    except Exception:
                        pass
                if word is not None:
                    try:
                        word.Quit()
                    except Exception:
                        pass
        if DOCX2PDF_AVAILABLE:
            try:
                docx2pdf_convert(i, o)
                return True
            except Exception as e:
                self.log(f"docx2pdf-Konvertierung fehlgeschlagen: {e}")
        else:
            self.log(LOG_MSG_WORD_UNAVAILABLE)
        return False

    def convert_img(self, i, o):
        if not OCR_AVAILABLE:
            self.log("Bild-Konvertierung nicht verfügbar (reportlab/Pillow fehlt).")
            return False
        try:
            img = Image.open(i).convert("RGB")
            c = canvas.Canvas(o)
            c.setPageSize((img.width, img.height))
            c.drawImage(ImageReader(img), 0, 0, width=img.width, height=img.height)
            c.save()
            return True
        except Exception as e:
            self.log(f"Bild-Konvertierung fehlgeschlagen: {e}")
            return False

    def convert_txt(self, i, o):
        if not OCR_AVAILABLE:
            self.log("TXT-Konvertierung nicht verfügbar (reportlab fehlt).")
            return False
        try:
            c = canvas.Canvas(o, pagesize=A4)
            t = c.beginText(20*mm, A4[1]-20*mm)
            t.setFont("Helvetica", 10)
            with open(i, "r", encoding="utf-8", errors="replace") as f:
                for line in f:
                    t.textLine(line.strip())
            c.drawText(t)
            c.save()
            return True
        except Exception as e:
            self.log(f"TXT-Konvertierung fehlgeschlagen: {e}")
            return False

class OCRProcessor:
    def __init__(self, log_func=print): self.log = log_func
    def has_text(self, p):
        try:
            r = PdfReader(p)
            t = ""
            for pg in r.pages:
                x = pg.extract_text()
                if x:
                    t += x
            return len(t.strip()) > 50
        except Exception as e:
            self.log(f"Text-Erkennung fehlgeschlagen: {e}")
            return False
    def add_text_layer(self, p):
        if not OCR_AVAILABLE:
            self.log(LOG_MSG_OCR_UNAVAILABLE)
            return False, "No OCR"
        try:
            tmp = p.with_suffix(".temp.pdf")
            imgs = convert_from_path(str(p), poppler_path=POPPLER_PATH)
            w = PdfWriter()
            for i in imgs:
                b = pytesseract.image_to_pdf_or_hocr(i, extension='pdf', lang='deu+eng')
                w.add_page(PdfReader(io.BytesIO(b)).pages[0])
            with open(tmp, "wb") as f:
                w.write(f)
            shutil.move(tmp, p)
            return True, "OK"
        except Exception as e:
            self.log(f"OCR-Verarbeitung fehlgeschlagen: {e}")
            tmp.unlink(missing_ok=True)
            return False, str(e)

# ==================== IMAP WORKER ====================

_IMAP_MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
                "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


class GrabberWorker(QThread):
    log = Signal(str)
    finished = Signal()
    progress = Signal(int, int)

    def __init__(self, profiles, accounts, global_settings, base_path, db, date_override=None):
        super().__init__()
        self.profiles = profiles
        self.accounts = {a.name: a for a in accounts} # Map for fast lookup
        self.global_settings = global_settings
        self.base_path = base_path
        self.db = db
        self.date_override = date_override # datetime object
        self.converter = UniversalConverter(lambda x: self.log.emit(x))
        self.ocr = OCRProcessor(lambda x: self.log.emit(x))

    def get_effective_settings(self, profile):
        if profile.override_settings: return profile.override_settings
        return self.global_settings

    @staticmethod
    def _quote_imap_string(value: str) -> str:
        """Maskiert einen String für IMAP-Suchargumente und bereinigt Newlines."""
        cleaned = re.sub(r'[\r\n]+', ' ', value or "").strip()
        escaped = cleaned.replace("\\", "\\\\").replace('"', '\\"').strip()
        return f'"{escaped}"'

    def _get_since_date(self, profile) -> Optional[datetime]:
        """Ermittelt das effektive Startdatum aus Globalfilter oder Profil."""
        if self.date_override:
            return self.date_override
        if profile.query_since:
            try:
                return datetime.strptime(profile.query_since.strip(), "%Y-%m-%d")
            except (ValueError, TypeError):
                return None
        return None

    def _supports_gmail_raw(self, conn) -> bool:
        """Prüft, ob der IMAP-Server Gmails X-GM-RAW-Syntax anbietet."""
        capabilities = getattr(conn, "capabilities", ()) or ()
        normalized = {
            cap.decode("ascii", errors="ignore").upper() if isinstance(cap, bytes) else str(cap).upper()
            for cap in capabilities
        }
        return "X-GM-EXT-1" in normalized

    def build_imap_search_args(self, profile) -> List[str]:
        """Baut Standard-IMAP-Suchkriterien als Argumentliste."""
        criteria: List[str] = []
        sender = (profile.query_sender or "").strip()
        if sender:
            criteria.extend(["FROM", self._quote_imap_string(sender)])
        subject = (profile.query_subject or "").strip()
        if subject:
            criteria.extend(["SUBJECT", self._quote_imap_string(subject)])

        since_date = self._get_since_date(profile)
        if since_date:
            criteria.extend([
                "SINCE",
                f"{since_date.day:02d}-{_IMAP_MONTHS[since_date.month - 1]}-{since_date.year}"
            ])

        return criteria or ["ALL"]

    def build_gmail_raw_query(self, profile) -> str:
        """Kombiniert gespeicherte Gmail-Query mit den Standardfiltern."""
        parts = []
        gmail_q = (profile.gmail_query or "").strip()
        if gmail_q:
            parts.append(gmail_q)
        sender = (profile.query_sender or "").strip()
        if sender:
            parts.append(f'from:{self._quote_imap_string(sender)}')
        subject = (profile.query_subject or "").strip()
        if subject:
            parts.append(f'subject:{self._quote_imap_string(subject)}')

        since_date = self._get_since_date(profile)
        if since_date:
            parts.append(f"after:{since_date.strftime('%Y/%m/%d')}")

        return " ".join(part for part in parts if part).strip()

    def connect_imap(self, acc_name):
        acc = self.accounts.get(acc_name)
        if not acc:
            self.log.emit(f"❌ Account '{acc_name}' nicht gefunden.")
            return None

        pwd = keyring.get_password(APP_NAME, acc.name) if KEYRING_AVAIL else None
        if not pwd:
            self.log.emit(f"❌ Kein Passwort für '{acc.name}'.")
            return None

        try:
            conn = imaplib.IMAP4_SSL(acc.host, acc.port, timeout=30)
            conn.login(acc.user, pwd)
            conn.select(acc.search_folder, readonly=True)
            return conn
        except Exception as e:
            self.log.emit(f"❌ IMAP Fehler ({acc.name}): {e}")
            return None

    def run(self):
        total = len(self.profiles)

        # Group profiles by account to reuse connection
        profiles_by_acc = {}
        for p in self.profiles:
            if not p.active: continue
            if p.account_name not in profiles_by_acc: profiles_by_acc[p.account_name] = []
            profiles_by_acc[p.account_name].append(p)

        processed_count = 0

        for acc_name, profs in profiles_by_acc.items():
            if self.isInterruptionRequested(): break

            self.log.emit(f"🔌 Verbinde mit {acc_name}...")
            conn = self.connect_imap(acc_name)
            if not conn: continue

            for profile in profs:
                if self.isInterruptionRequested(): break
                self.progress.emit(processed_count, total)
                processed_count += 1

                self.log.emit(f"🚀 Profil: {profile.name}")
                self.process_profile(conn, profile, self.get_effective_settings(profile))

            try: conn.logout()
            except (OSError, imaplib.IMAP4.error): pass

        if self.global_settings.enable_hash_check:
            self.run_deduplication()

        self.progress.emit(total, total)
        self.finished.emit()

    def process_profile(self, conn, profile, settings):
        folder_name = profile.target_folder if profile.target_folder else profile.name
        dl_dir = self.base_path / sanitize_filename(folder_name)
        dl_dir.mkdir(parents=True, exist_ok=True)

        try:
            gmail_query = self.build_gmail_raw_query(profile)
            if gmail_query and self._supports_gmail_raw(conn):
                search_args = (None, "X-GM-RAW", self._quote_imap_string(gmail_query))
            else:
                if gmail_query:
                    self.log.emit("   Gmail-Query gespeichert, aber Server unterstützt kein X-GM-RAW. Fallback auf IMAP-Filter.")
                search_args = (None, *self.build_imap_search_args(profile))

            # UIDs statt MSN nutzen — stabil gegenüber parallelen Expunges
            typ, data = conn.uid('search', *search_args[1:])
            if typ != 'OK': return

            ids = data[0].split()
            if not ids:
                self.log.emit(LOG_MSG_NO_MAILS)
                return

            # Limit to last 30 to avoid overflow
            ids = ids[-30:]

            for num in ids:
                if self.isInterruptionRequested(): break
                self.process_email(conn, num, dl_dir, settings, profile.name)

        except Exception as e:
            self.log.emit(f"   ❌ Suchfehler: {e}")

    def _parse_email_metadata(self, msg):
        """Extrahiert Absender, Betreff und Datum aus einer E-Mail."""
        subject = decode_header_str(msg["Subject"])
        sender = decode_header_str(msg["From"])
        if "<" in sender:
            display_name = sender.split("<")[0].strip().replace('"', '')
            if display_name:
                sender = display_name
            else:
                addr_match = re.search(r'<([^>]+)>', sender)
                sender = addr_match.group(1).strip() if addr_match else sender

        date_iso = None
        date_header = msg.get("Date")
        if date_header:
            try:
                date_tuple = email.utils.parsedate_tz(date_header)
                if date_tuple:
                    year, month, day = date_tuple[0], date_tuple[1], date_tuple[2]
                    if 1900 <= year <= 2100 and 1 <= month <= 12 and 1 <= day <= 31:
                        date_iso = f"{year:04d}-{month:02d}-{day:02d}"
                    else:
                        ts = email.utils.mktime_tz(date_tuple)
                        if ts >= 0:
                            date_iso = datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
            except (OSError, OverflowError, ValueError, TypeError):
                pass
        if not date_iso:
            date_iso = datetime.now().strftime("%Y-%m-%d")
        return sender, subject, date_iso

    def _auto_categorize(self, sender: str, subject: str, settings: 'DownloadSettings') -> Optional[str]:
        """
        Bestimmt einen Unterordner basierend auf Absender und Betreff.

        Regeln in settings.category_rules (Liste von Dicts):
          {"keyword": "rechnung", "folder": "Rechnungen", "match": "subject|sender|both"}
          {"keyword": "amazon", "folder": "Amazon", "match": "sender"}

        Falls keine Regel greift: Default-Regeln (Rechnung, Versand, Vertrag, etc.)
        Falls auto_categorize=False: None (keine Kategorisierung)
        """
        if not settings.auto_categorize:
            return None

        text_subject = (subject or "").lower()
        text_sender = (sender or "").lower()

        # Benutzerdefinierte Regeln zuerst
        for rule in (settings.category_rules or []):
            kw = rule.get("keyword", "").lower()
            folder = rule.get("folder", "")
            match_field = rule.get("match", "both")
            if not kw or not folder:
                continue

            matched = False
            if match_field in ("subject", "both") and kw in text_subject:
                matched = True
            if match_field in ("sender", "both") and kw in text_sender:
                matched = True
            if matched:
                return folder

        # Default-Regeln
        default_rules = [
            (["rechnung", "invoice", "billing", "zahlungsbeleg"], "Rechnungen"),
            (["versand", "lieferung", "tracking", "sendung", "shipping"], "Versand"),
            (["vertrag", "verträge", "contract", "contracts", "vereinbarung"], "Verträge"),
            (["kuendigung", "kündigung", "cancellation", "storno"], "Kündigungen"),
            (["steuer", "finanzamt", "elster", "tax"], "Steuer"),
            (["versicherung", "insurance", "police"], "Versicherung"),
            (["bewerbung", "application", "stellenangebot"], "Bewerbungen"),
            (["kontoauszug", "account statement", "bankbeleg"], "Bank"),
        ]

        combined = text_subject + " " + text_sender
        for keywords, folder in default_rules:
            if any(kw in combined for kw in keywords):
                return folder

        return None

    def _save_attachment(self, part, base_name, dl_dir, settings, profile_name,
                         date_iso, sender, subject, attachment_index: int = 1):
        """Speichert einen Anhang, konvertiert optional zu PDF und fuehrt OCR durch."""
        raw_filename = part.get_filename()
        if not raw_filename:
            return False
        filename = decode_header_str(raw_filename)
        ext = Path(filename).suffix.lower().replace(".", "")
        if not (settings.download_attachments and ext in settings.formats):
            return False
        payload = part.get_payload(decode=True)
        if payload is None:
            return False

        orig_stem = sanitize_filename(Path(filename).stem)
        candidate_name = f"{base_name}_ATT.{ext}"
        if attachment_index > 1 or (dl_dir / candidate_name).exists():
            candidate_name = f"{base_name}_ATT_{attachment_index}_{orig_stem}.{ext}"
            if (dl_dir / candidate_name).exists():
                candidate_name = f"{base_name}_ATT_{attachment_index}.{ext}"

        final_path = dl_dir / candidate_name
        if final_path.exists():
            return False
        with open(final_path, "wb") as f:
            f.write(payload)
        self.log.emit(f"   💾 {candidate_name}")
        # Convert / OCR
        proc_path = final_path
        if settings.convert_all_to_pdf and ext != "pdf":
            pdf = self.converter.convert_to_pdf(final_path)
            if pdf:
                proc_path = pdf
                if not settings.keep_original_after_convert:
                    os.remove(final_path)
        if proc_path.suffix.lower() == ".pdf" and OCR_AVAILABLE:
            if not self.ocr.has_text(proc_path):
                self.log.emit(LOG_MSG_OCR_PROCESSING)
                self.ocr.add_text_layer(proc_path)
        self.add_db(profile_name, proc_path.name, date_iso, str(proc_path), sender, subject)
        return True

    def _convert_body_to_pdf(self, msg, base_name, dl_dir, profile_name,
                             date_iso, sender, subject):
        """Konvertiert den E-Mail-Body (HTML oder Text) in ein PDF.

        Bevorzugt text/html; fällt auf text/plain zurück, das als <pre>-Block
        gewrappt wird. Gibt None zurück wenn kein Body gefunden wurde.
        """
        import html as html_mod
        body_content = ""
        if msg.is_multipart():
            # Zuerst HTML suchen (nur Nicht-Anhänge)
            for part in msg.walk():
                if part.get_filename() or part.get_content_disposition() == "attachment":
                    continue
                if part.get_content_type() == "text/html":
                    _payload = part.get_payload(decode=True)
                    if _payload is None:
                        continue
                    body_content = safe_decode_payload(_payload, part.get_content_charset())
                    break
            # Fallback: Plain-Text (nur Nicht-Anhänge)
            if not body_content:
                for part in msg.walk():
                    if part.get_filename() or part.get_content_disposition() == "attachment":
                        continue
                    if part.get_content_type() == "text/plain":
                        _payload = part.get_payload(decode=True)
                        if _payload is None:
                            continue
                        raw = safe_decode_payload(_payload, part.get_content_charset())
                        body_content = f"<pre>{html_mod.escape(raw)}</pre>"
                        break
        else:
            if not (msg.get_filename() or msg.get_content_disposition() == "attachment"):
                ct = msg.get_content_type()
                if ct == "text/html":
                    _payload = msg.get_payload(decode=True)
                    if _payload is not None:
                        body_content = safe_decode_payload(_payload, msg.get_content_charset())
                elif ct == "text/plain":
                    _payload = msg.get_payload(decode=True)
                    if _payload is not None:
                        raw = safe_decode_payload(_payload, msg.get_content_charset())
                        body_content = f"<pre>{html_mod.escape(raw)}</pre>"
        if not body_content:
            return
        if not PISA_AVAILABLE:
            self.log.emit("   Body->PDF nicht möglich (xhtml2pdf fehlt).")
            return
        pdf_target = dl_dir / f"{base_name}_MAIL.pdf"
        if pdf_target.exists():
            return
        result = None
        try:
            with open(pdf_target, "wb") as f:
                result = pisa.CreatePDF(body_content, dest=f)
            if result and result.err:
                self.log.emit(f"   PDF-Erstellung fehlgeschlagen (pisa err={result.err}).")
                pdf_target.unlink(missing_ok=True)
                return
            self.log.emit(f"   📄 Mail->PDF: {pdf_target.name}")
            self.add_db(profile_name, pdf_target.name, date_iso, str(pdf_target), sender, subject)
        except Exception as e:
            self.log.emit(f"   PDF-Erstellung fehlgeschlagen: {e}")
            pdf_target.unlink(missing_ok=True)

    def process_email(self, conn, num, dl_dir, settings, profile_name):
        try:
            res, data = conn.uid('fetch', num, '(RFC822)')
            if res != 'OK':
                return
            if not data or data[0] is None:
                return
            msg = email.message_from_bytes(data[0][1])
            sender, subject, date_iso = self._parse_email_metadata(msg)
            base_name = f"{date_iso}__{sanitize_filename(sender)}__{sanitize_filename(subject)}"

            # Auto-Kategorisierung: ggf. Unterordner bestimmen
            category = self._auto_categorize(sender, subject, settings)
            target_dir = dl_dir
            if category:
                target_dir = dl_dir / sanitize_filename(category)
                target_dir.mkdir(parents=True, exist_ok=True)

            att_found = False
            att_counter = 0
            for part in msg.walk():
                if part.get_content_maintype() == 'multipart':
                    continue
                # Anhänge zuverlässig erkennen, auch wenn Content-Disposition None oder inline ist
                if not part.get_filename():
                    continue
                att_counter += 1
                if self._save_attachment(part, base_name, target_dir, settings,
                                         profile_name, date_iso, sender, subject,
                                         attachment_index=att_counter):
                    att_found = True

            do_body = settings.convert_body_to_pdf
            if not do_body and not att_found:
                do_body = True
            if do_body:
                self._convert_body_to_pdf(msg, base_name, target_dir, profile_name,
                                          date_iso, sender, subject)
        except Exception as e:
            self.log.emit(f"Mail Parse Error: {e}")

    def run_deduplication(self):
        self.log.emit(LOG_MSG_DEDUP_START)
        hashes = {}
        deleted = 0
        deleted_paths = set()
        files = [f for f in self.base_path.rglob("*") if f.is_file()]
        for f in files:
            if self.isInterruptionRequested(): break
            h = calculate_file_hash(f)
            if not h: continue
            if h in hashes:
                try:
                    os.remove(f)
                    deleted += 1
                    deleted_paths.add(str(f))
                    self.log.emit(f"   Duplikat entfernt: {f.name}")
                except (OSError, PermissionError): pass
            else: hashes[h] = f
        if deleted_paths:
            self.db[:] = [d for d in self.db if d.path not in deleted_paths]
        self.log.emit(f"🧹 Fertig. {deleted} gelöscht.")

    def add_db(self, prof, fname, date, path, snd, sub):
        doc = Document(prof, fname, date, path, snd, sub)
        if not any(d.path == doc.path for d in self.db): self.db.insert(0, doc)

# ==================== GUI DIALOGS ====================

class QueryBuilderDialog(QDialog):
    """Dialog zum interaktiven Aufbau von Gmail/IMAP-ähnlichen Suchabfragen.

    Ermöglicht die Zusammenstellung einer Suchquery über Absender, Betreff,
    Zeitraum und Anhang-Filter ohne manuelle Texteingabe.
    Das Ergebnis ist über get_query() als String abrufbar.
    """

    def __init__(self, current_query="", parent=None):
        super().__init__(parent)
        self.setWindowTitle("Query Builder")
        self.resize(500, 400)

        layout = QVBoxLayout(self)

        g_scope = QGroupBox("1. Wo suchen?")
        gl = QHBoxLayout(g_scope)
        self.rb_all = QRadioButton("Überall (außer Müll)"); self.rb_all.setChecked(True)
        self.rb_inbox = QRadioButton("Nur Inbox")
        self.rb_sent = QRadioButton("Gesendet")
        self.rb_trash = QRadioButton("Auch Papierkorb")
        gl.addWidget(self.rb_all); gl.addWidget(self.rb_inbox)
        gl.addWidget(self.rb_sent); gl.addWidget(self.rb_trash)
        layout.addWidget(g_scope)

        g_date = QGroupBox("2. Zeitraum")
        gd = QGridLayout(g_date)
        self.cb_time = QComboBox()
        self.cb_time.addItems(["Alles", "Dieses Jahr", "Letztes Jahr", "Benutzerdefiniert"])
        self.cb_time.currentIndexChanged.connect(self.toggle_dates)

        self.de_from = QDateEdit(QDate.currentDate().addYears(-1)); self.de_from.setCalendarPopup(True)
        self.de_to = QDateEdit(QDate.currentDate()); self.de_to.setCalendarPopup(True)
        self.de_from.setEnabled(False); self.de_to.setEnabled(False)

        gd.addWidget(QLabel("Preset:"), 0, 0); gd.addWidget(self.cb_time, 0, 1)
        gd.addWidget(QLabel("Von:"), 1, 0); gd.addWidget(self.de_from, 1, 1)
        gd.addWidget(QLabel("Bis:"), 2, 0); gd.addWidget(self.de_to, 2, 1)
        layout.addWidget(g_date)

        g_crit = QGroupBox("3. Kriterien (Komma für ODER)")
        gc = QGridLayout(g_crit)
        self.inp_from = QLineEdit(); self.inp_from.setPlaceholderText("z.B. allianz, tk, aok")
        self.inp_sub = QLineEdit(); self.inp_sub.setPlaceholderText("z.B. Rechnung, Invoice, Payment")
        self.chk_att = QCheckBox("Muss Anhang haben (has:attachment)"); self.chk_att.setChecked(True)

        gc.addWidget(QLabel("Absender:"), 0, 0); gc.addWidget(self.inp_from, 0, 1)
        gc.addWidget(QLabel("Betreff:"), 1, 0); gc.addWidget(self.inp_sub, 1, 1)
        gc.addWidget(self.chk_att, 2, 0, 1, 2)
        layout.addWidget(g_crit)

        self.res_query = QLineEdit(current_query)
        self.res_query.setPlaceholderText("Ergebnis Query...")
        b_gen = QPushButton("Generieren"); b_gen.clicked.connect(self.generate)
        layout.addWidget(b_gen); layout.addWidget(self.res_query)

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject)
        layout.addWidget(bb)

    def toggle_dates(self):
        is_custom = self.cb_time.currentText() == "Benutzerdefiniert"
        self.de_from.setEnabled(is_custom)
        self.de_to.setEnabled(is_custom)

    @staticmethod
    def _parse_comma_separated_input(prefix, text):
        """Konvertiert Komma-separierte Eingabe zu Query-Syntax.

        Args:
            prefix: Query-Prefix (z.B. "from", "subject")
            text: Benutzereingabe (z.B. "allianz, tk, aok" oder "Telekom Deutschland, Allianz Global")

        Returns:
            str oder None: Query-Teil (z.B. "from:(\"Telekom Deutschland\" OR \"Allianz Global\")")
        """
        if not text:
            return None
        raw_terms = [t.strip() for t in text.split(",") if t.strip()]
        if not raw_terms:
            return None
        formatted_terms = []
        for t in raw_terms:
            if " " in t and not (t.startswith('"') and t.endswith('"')):
                formatted_terms.append(f'"{t}"')
            else:
                formatted_terms.append(t)
        if len(formatted_terms) > 1:
            joined = " OR ".join(formatted_terms)
            return f"{prefix}:({joined})"
        else:
            return f"{prefix}:{formatted_terms[0]}"

    def generate(self):
        parts = []
        if self.rb_inbox.isChecked(): parts.append("in:inbox")
        elif self.rb_sent.isChecked(): parts.append("in:sent")
        elif self.rb_trash.isChecked(): parts.append("in:trash")
        else:
            parts.append("-in:trash")

        today = date.today()
        t = self.cb_time.currentText()
        d_from = None; d_to = None

        if t == "Dieses Jahr": d_from = date(today.year, 1, 1)
        elif t == "Letztes Jahr": d_from = date(today.year - 1, 1, 1); d_to = date(today.year - 1, 12, 31)
        elif t == "Benutzerdefiniert": d_from = self.de_from.date().toPyDate(); d_to = self.de_to.date().toPyDate()

        if d_from: parts.append(f"after:{d_from.strftime('%Y/%m/%d')}")
        if d_to: parts.append(f"before:{d_to.strftime('%Y/%m/%d')}")

        f = self._parse_comma_separated_input("from", self.inp_from.text())
        if f: parts.append(f)

        s = self._parse_comma_separated_input("subject", self.inp_sub.text())
        if s: parts.append(s)

        if self.chk_att.isChecked(): parts.append("has:attachment")

        self.res_query.setText(" ".join(parts))

    def get_query(self):
        return self.res_query.text()


class AccountDialog(QDialog):
    def __init__(self, acc=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(UI_TITLE_ACCOUNT_DIALOG)
        layout = QFormLayout(self)
        self.n = QLineEdit(acc.name if acc else "")
        self.h = QLineEdit(acc.host if acc else "imap.gmx.net")
        self.u = QLineEdit(acc.user if acc else "")
        self.p = QSpinBox(); self.p.setRange(1, 65535); self.p.setValue(acc.port if acc else 993)
        self.f = QLineEdit(acc.search_folder if acc else "INBOX")
        self.pw = QLineEdit(); self.pw.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addRow("Name:", self.n); layout.addRow("Host:", self.h); layout.addRow("Port:", self.p)
        layout.addRow("User:", self.u); layout.addRow("Folder:", self.f); layout.addRow("Passwort:", self.pw)

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject); layout.addRow(bb)

    def get_data(self):
        return MailAccount(self.n.text(), self.h.text(), self.u.text(), self.p.value(), self.f.text()), self.pw.text()

class ProfileDialog(QDialog):
    def __init__(self, accounts, profile=None, global_settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle(UI_TITLE_PROFILE_DIALOG)
        self.resize(500, 600)
        self.global_settings = global_settings

        lay = QVBoxLayout(self)
        gb_base = QGroupBox(UI_LABEL_BASIS)
        l_base = QFormLayout(gb_base)

        self.inp_name = QLineEdit(profile.name if profile else "")
        self.inp_group = QLineEdit(profile.group if profile else DEFAULT_GROUP)
        self.cb_acc = QComboBox(); self.cb_acc.addItems([a.name for a in accounts])
        if profile: self.cb_acc.setCurrentText(profile.account_name)

        self.inp_subj = QLineEdit(profile.query_subject if profile else "")
        self.inp_send = QLineEdit(profile.query_sender if profile else "")

        # Gmail-Query Freitext + Query Builder Button
        self.inp_gmail_query = QLineEdit(profile.gmail_query if profile else "")
        self.inp_gmail_query.setPlaceholderText("z.B. from:amazon has:attachment after:2024/01/01")
        b_builder = QPushButton("Builder ...")
        b_builder.setToolTip("Query Builder öffnen")
        b_builder.clicked.connect(self._open_query_builder)
        h_query = QHBoxLayout()
        h_query.addWidget(self.inp_gmail_query)
        h_query.addWidget(b_builder)

        self.inp_folder = QLineEdit(profile.target_folder if profile else "")
        self.chk_active = QCheckBox("Aktiv"); self.chk_active.setChecked(profile.active if profile else True)

        l_base.addRow("Name:", self.inp_name); l_base.addRow("Gruppe:", self.inp_group)
        l_base.addRow("Account:", self.cb_acc)
        l_base.addRow("Betreff:", self.inp_subj); l_base.addRow("Absender:", self.inp_send)
        l_base.addRow("Gmail-Query (optional):", h_query)
        l_base.addRow("Zielordner:", self.inp_folder); l_base.addRow(self.chk_active)
        lay.addWidget(gb_base)

        # Override Settings (identisch zu V6)
        gb_over = QGroupBox(UI_LABEL_SETTINGS_OVERRIDE); gb_over.setCheckable(True); gb_over.setChecked(bool(profile and profile.override_settings))
        self.gb_over = gb_over
        l_over = QFormLayout(gb_over)
        defs = profile.override_settings if (profile and profile.override_settings) else self.global_settings
        self.chk_att = QCheckBox("Anhänge"); self.chk_att.setChecked(defs.download_attachments)
        self.chk_conv = QCheckBox("Body -> PDF"); self.chk_conv.setChecked(defs.convert_body_to_pdf)
        self.chk_all = QCheckBox("Alles -> PDF"); self.chk_all.setChecked(defs.convert_all_to_pdf)
        self.inp_fmt = QLineEdit(", ".join(defs.formats))
        l_over.addRow(self.chk_att); l_over.addRow(self.chk_conv); l_over.addRow(self.chk_all); l_over.addRow("Formate:", self.inp_fmt)
        lay.addWidget(gb_over)

        self._existing_id = profile.id if profile else None

        bb = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel)
        bb.accepted.connect(self.accept); bb.rejected.connect(self.reject); lay.addWidget(bb)

    def _open_query_builder(self):
        """Öffnet den QueryBuilderDialog und überträgt das Ergebnis in das Query-Feld."""
        d = QueryBuilderDialog(self.inp_gmail_query.text(), self)
        if d.exec():
            self.inp_gmail_query.setText(d.get_query())

    def get_profile(self):
        pid = self._existing_id if self._existing_id else str(time.time())
        over = None
        if self.gb_over.isChecked():
            fmts = [x.strip() for x in self.inp_fmt.text().split(",") if x.strip()]
            over = DownloadSettings(
                download_attachments=self.chk_att.isChecked(),
                convert_body_to_pdf=self.chk_conv.isChecked(),
                convert_all_to_pdf=self.chk_all.isChecked(),
                formats=fmts,
            )
        return SearchProfile(pid, self.inp_name.text(), self.inp_group.text(), self.cb_acc.currentText(),
                             self.inp_subj.text(), self.inp_send.text(), "", self.inp_folder.text(),
                             self.chk_active.isChecked(), over, self.inp_gmail_query.text())

# ==================== MAIN WINDOW ====================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.profiles = []
        self.accounts = []
        self.global_settings = DownloadSettings()
        self.documents = []
        self.base_path = str(Path.home() / "Downloads" / "UnivDocs")
        self.worker = None
        self.scheduler_interval = 0  # 0 = deaktiviert, sonst Minuten
        self._scheduler_timer = QTimer(self)
        self._scheduler_timer.timeout.connect(self._on_scheduler_tick)
        self.load_config()
        self.setup_ui()
        self._apply_scheduler()

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                d = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
                self.base_path = d.get("base_path", self.base_path)
                self.global_settings = DownloadSettings.from_dict(d.get("global_settings", {}))
                self.profiles = [SearchProfile.from_dict(x) for x in d.get("profiles", [])]
                self.accounts = [MailAccount.from_dict(x) for x in d.get("accounts", [])]
                self.scheduler_interval = d.get("scheduler_interval", 0)
            except Exception as e:
                logger.warning(f"load_config (config): {e}")
        if DOCS_DB.exists():
            try: self.documents = [Document.from_dict(x) for x in json.loads(DOCS_DB.read_text(encoding="utf-8"))]
            except Exception as e:
                logger.warning(f"load_config (docs db): {e}")

    def save_config(self):
        d = {
            "base_path": self.base_path,
            "global_settings": self.global_settings.to_dict(),
            "profiles": [p.to_dict() for p in self.profiles],
            "accounts": [a.to_dict() for a in self.accounts],
            "scheduler_interval": self.scheduler_interval
        }
        CONFIG_FILE.write_text(json.dumps(d, indent=4), encoding="utf-8")
        DOCS_DB.write_text(json.dumps([x.to_dict() for x in self.documents], indent=4), encoding="utf-8")

    def setup_ui(self):
        self.setWindowTitle(APP_NAME)
        icon = get_app_icon()
        if icon and not icon.isNull():
            self.setWindowIcon(icon)
        self.resize(1200, 800)
        p = self.palette(); p.setColor(QPalette.ColorRole.Window, QColor(45, 45, 45)); p.setColor(QPalette.ColorRole.WindowText, Qt.GlobalColor.white); p.setColor(QPalette.ColorRole.Base, QColor(30, 30, 30)); p.setColor(QPalette.ColorRole.Text, Qt.GlobalColor.white); p.setColor(QPalette.ColorRole.Button, QColor(60, 60, 60)); p.setColor(QPalette.ColorRole.ButtonText, Qt.GlobalColor.white); self.setPalette(p)

        cw = QWidget(); self.setCentralWidget(cw); lay = QHBoxLayout(cw)

        # LEFT
        left = QWidget(); l1 = QVBoxLayout(left)
        gb_d = QGroupBox(UI_LABEL_TIME_FILTER)
        gh = QHBoxLayout(gb_d)
        self.cb_time = QComboBox(); self.cb_time.addItems(["Alles", "Ab diesem Jahr", "Ab letztem Jahr", "Ab letztem Monat"])
        self.cb_time.setToolTip("Zeitraum für den nächsten Profil-Lauf wählen")
        self.cb_time.setAccessibleName("Zeitraum auswählen")
        self.cb_time.setAccessibleDescription("Filtert den nächsten Lauf auf einen vordefinierten Zeitraum.")
        gh.addWidget(self.cb_time); l1.addWidget(gb_d)

        self.btn_start = QPushButton(UI_BTN_START); self.btn_start.setMinimumHeight(50)
        self.btn_start.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; font-size: 14pt;")
        self.btn_start.setToolTip("Alle aktiven Profile nacheinander ausführen")
        self.btn_start.setAccessibleName("Alle Profile starten")
        self.btn_start.clicked.connect(self.run_all)
        l1.addWidget(self.btn_start)

        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Profil", "Account"])
        self.tree.setAccessibleName("Profile")
        self.tree.setToolTip("Suchprofile per Doppelklick bearbeiten oder per Drag-and-drop sortieren")
        self.tree.itemDoubleClicked.connect(self.edit_prof)
        # Drag&Drop Profil-Sortierung
        self.tree.setDragEnabled(True)
        self.tree.setAcceptDrops(True)
        self.tree.setDropIndicatorShown(True)
        self.tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self.tree.model().rowsMoved.connect(self._sync_profile_order)
        self.tree.currentItemChanged.connect(self._update_profile_delete_action_state)
        l1.addWidget(self.tree)

        h_btn = QHBoxLayout(); self.btn_add_profile = QPushButton(UI_BTN_ADD_PROFILE); self.btn_add_profile.clicked.connect(self.add_prof); h_btn.addWidget(self.btn_add_profile)
        self.btn_add_profile.setToolTip("Neues Suchprofil anlegen")
        self.btn_add_profile.setAccessibleName("Profil hinzufügen")
        self.btn_add_profile.setAccessibleDescription("Öffnet den Dialog zum Anlegen eines neuen Suchprofils.")
        self.btn_delete_profile = QPushButton(UI_BTN_DELETE_PROFILE); self.btn_delete_profile.clicked.connect(self.del_prof); h_btn.addWidget(self.btn_delete_profile)
        self.btn_delete_profile.setToolTip("Ausgewähltes Suchprofil löschen")
        self.btn_delete_profile.setAccessibleName("Profil löschen")
        self.btn_delete_profile.setAccessibleDescription("Löscht das aktuell ausgewählte Suchprofil.")
        l1.addLayout(h_btn); lay.addWidget(left, stretch=1)

        # RIGHT
        self.tabs = QTabWidget()
        self.tabs.setAccessibleName("Hauptnavigation")

        # Accounts Tab
        t_acc = QWidget(); la = QVBoxLayout(t_acc)
        self.list_acc = QTableWidget(0, 3); self.list_acc.setHorizontalHeaderLabels(["Name", "Host", "User"]); self.list_acc.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.list_acc.setAccessibleName("Accounts")
        self.list_acc.itemSelectionChanged.connect(self._update_account_delete_action_state)
        la.addWidget(self.list_acc)
        ha = QHBoxLayout(); self.btn_add_account = QPushButton(UI_BTN_ADD_ACCOUNT); self.btn_add_account.clicked.connect(self.add_acc); ha.addWidget(self.btn_add_account)
        self.btn_add_account.setToolTip("Neuen IMAP-Account anlegen")
        self.btn_add_account.setAccessibleName("Account hinzufügen")
        self.btn_add_account.setAccessibleDescription("Öffnet den Dialog zum Hinzufügen eines neuen IMAP-Accounts.")
        self.btn_delete_account = QPushButton(UI_BTN_DELETE_ACCOUNT); self.btn_delete_account.clicked.connect(self.del_acc); ha.addWidget(self.btn_delete_account); la.addLayout(ha)
        self.btn_delete_account.setToolTip("Ausgewählten IMAP-Account löschen")
        self.btn_delete_account.setAccessibleName("Account löschen")
        self.btn_delete_account.setAccessibleDescription("Löscht den aktuell ausgewählten IMAP-Account.")
        idx_accounts = self.tabs.addTab(t_acc, UI_TAB_ACCOUNTS)
        self.tabs.setTabToolTip(idx_accounts, "IMAP-Konten verwalten")

        # Docs Tab
        t_doc = QWidget(); ld = QVBoxLayout(t_doc)
        self.table = QTableWidget(0, 5); self.table.setHorizontalHeaderLabels(["Datum", "Profil", "Absender", "Datei", "Pfad"]); self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.table.setAccessibleName("Dokumente")
        self.table.cellDoubleClicked.connect(self.open_doc)
        ld.addWidget(self.table)
        idx_docs = self.tabs.addTab(t_doc, UI_TAB_DOCS)
        self.tabs.setTabToolTip(idx_docs, "Gefundene Dokumente anzeigen und öffnen")

        # Settings Tab
        t_set = QWidget(); ls = QVBoxLayout(t_set)
        g = QGroupBox(UI_LABEL_GLOBAL)
        fl = QFormLayout(g)
        self.ip_path = QLineEdit(self.base_path)
        self.ip_path.setToolTip("Lokalen Zielordner für heruntergeladene Dokumente ändern")
        self.ip_path.setAccessibleName("Download-Pfad")
        self.ip_path.setAccessibleDescription("Zeigt den lokalen Zielordner für heruntergeladene Dokumente.")
        self.btn_browse_path = QPushButton(UI_BTN_BROWSE_PATH); self.btn_browse_path.clicked.connect(self.brws)
        self.btn_browse_path.setToolTip("Zielordner für Downloads auswählen")
        self.btn_browse_path.setAccessibleName("Download-Ordner auswählen")
        hp = QHBoxLayout(); hp.addWidget(self.ip_path); hp.addWidget(self.btn_browse_path)
        self.ck_att = QCheckBox("Anhänge"); self.ck_att.setChecked(self.global_settings.download_attachments)
        self.ck_att.setToolTip("Lädt E-Mail-Anhänge aus passenden Nachrichten herunter")
        self.ck_att.setAccessibleName("Anhänge herunterladen")
        self.ck_att.setAccessibleDescription("Aktiviert oder deaktiviert den Download von Anhängen.")
        self.ck_pdf = QCheckBox("Body -> PDF"); self.ck_pdf.setChecked(self.global_settings.convert_body_to_pdf)
        self.ck_pdf.setToolTip("Wandelt Mail-Inhalte ohne Anhang zusätzlich in PDF-Dateien um")
        self.ck_pdf.setAccessibleName("Mail-Body als PDF speichern")
        self.ck_pdf.setAccessibleDescription("Erstellt aus dem E-Mail-Inhalt bei Bedarf eine PDF-Datei.")
        self.ck_hash = QCheckBox("Hash Dedupe"); self.ck_hash.setChecked(self.global_settings.enable_hash_check)
        self.ck_hash.setToolTip("Verhindert doppelte Dokumente über SHA-256-Vergleich")
        self.ck_hash.setAccessibleName("Hash-Deduplizierung")
        self.ck_hash.setAccessibleDescription("Überspringt doppelte Dokumente anhand ihres Hash-Werts.")
        self.ip_fmt = QLineEdit(", ".join(self.global_settings.formats))
        self.ip_fmt.setToolTip("Erlaubte Dateiformate als komma-getrennte Liste bearbeiten")
        self.ip_fmt.setAccessibleName("Erlaubte Formate")
        self.ip_fmt.setAccessibleDescription("Liste der Dateiformate, die heruntergeladen oder verarbeitet werden.")
        fl.addRow("Pfad:", hp); fl.addRow(self.ck_att); fl.addRow(self.ck_pdf); fl.addRow(self.ck_hash); fl.addRow("Formate:", self.ip_fmt)
        self.btn_save_settings = QPushButton("Speichern"); self.btn_save_settings.clicked.connect(self.save_glob); fl.addRow(self.btn_save_settings)
        self.btn_save_settings.setToolTip("Globale Download- und Format-Einstellungen speichern")
        self.btn_save_settings.setAccessibleName("Globale Einstellungen speichern")
        self.btn_save_settings.setAccessibleDescription("Speichert Pfad, Formate und Download-Optionen.")
        ls.addWidget(g)

        # Scheduler Settings
        gs = QGroupBox(UI_SCHEDULER_LABEL)
        sl = QFormLayout(gs)
        self.cb_scheduler = QComboBox()
        self.cb_scheduler.addItems(SCHEDULER_LABELS)
        self.cb_scheduler.setToolTip("Automatisches Prüfintervall für alle aktiven Profile wählen")
        self.cb_scheduler.setAccessibleName("Scheduler-Intervall")
        self.cb_scheduler.setAccessibleDescription("Legt fest, wie oft aktive Profile automatisch ausgeführt werden.")
        # Aktuellen Wert setzen
        if self.scheduler_interval in SCHEDULER_INTERVALS:
            self.cb_scheduler.setCurrentIndex(SCHEDULER_INTERVALS.index(self.scheduler_interval))
        self.lbl_scheduler_status = QLabel(UI_SCHEDULER_INACTIVE)
        self.lbl_scheduler_status.setStyleSheet("color: #888;")
        sl.addRow("Intervall:", self.cb_scheduler)
        sl.addRow("Status:", self.lbl_scheduler_status)
        self.btn_save_scheduler = QPushButton("Scheduler speichern")
        self.btn_save_scheduler.clicked.connect(self._save_scheduler)
        self.btn_save_scheduler.setToolTip("Automatisches Prüfintervall speichern")
        self.btn_save_scheduler.setAccessibleName("Scheduler speichern")
        self.btn_save_scheduler.setAccessibleDescription("Speichert das automatische Intervall für aktive Profile.")
        sl.addRow(self.btn_save_scheduler)
        ls.addWidget(gs)

        ge = QGroupBox(UI_EXPORT_LABEL)
        el = QVBoxLayout(ge)
        export_hint = QLabel(
            "Erstellt `docsgrabber-library-v1.json` für Web/PWA mit redigierten Profilen, Kategorien und Dokumentmetadaten."
        )
        export_hint.setWordWrap(True)
        self.btn_export_library = QPushButton(UI_BTN_EXPORT_LIBRARY)
        self.btn_export_library.clicked.connect(self.save_library_export)
        self.btn_export_library.setToolTip("Redigierten Companion-Export als JSON speichern")
        self.btn_export_library.setAccessibleName("Companion-Export speichern")
        el.addWidget(export_hint)
        el.addWidget(self.btn_export_library)
        ls.addWidget(ge)

        ls.addStretch(); idx_settings = self.tabs.addTab(t_set, UI_TAB_SETTINGS)
        self.tabs.setTabToolTip(idx_settings, "Globale Einstellungen und Scheduler konfigurieren")

        # Log
        t_log = QWidget(); ll = QVBoxLayout(t_log); self.log = QPlainTextEdit(); self.log.setReadOnly(True)
        self.log.setStyleSheet("font-family: Consolas; color: #DDD; background-color: #222;")
        self.log.setAccessibleName("Protokoll")
        ll.addWidget(self.log); idx_log = self.tabs.addTab(t_log, UI_TAB_LOG)
        self.tabs.setTabToolTip(idx_log, "Verarbeitungsprotokoll anzeigen")

        lay.addWidget(self.tabs, stretch=2)
        self.refresh_ui()

    def refresh_ui(self):
        # Accounts
        self.list_acc.setRowCount(0)
        for r, a in enumerate(self.accounts):
            self.list_acc.insertRow(r)
            self.list_acc.setItem(r, 0, QTableWidgetItem(a.name))
            self.list_acc.setItem(r, 1, QTableWidgetItem(a.host))
            self.list_acc.setItem(r, 2, QTableWidgetItem(a.user))

        # Profiles Tree
        self.tree.clear()
        groups = {}
        for p in self.profiles:
            g = p.group if p.group else DEFAULT_GROUP
            if g not in groups: groups[g] = []
            groups[g].append(p)
        for g, plist in groups.items():
            root = QTreeWidgetItem(self.tree)
            root.setText(0, f"📁 {g}")
            root.setExpanded(True)
            # Gruppen-Items nicht ziehbar machen (nur Profile sollen sortierbar sein)
            root.setFlags(root.flags() & ~Qt.ItemFlag.ItemIsDragEnabled)
            for p in plist:
                c = QTreeWidgetItem(root)
                c.setText(0, p.name)
                c.setText(1, p.account_name)
                c.setData(0, Qt.ItemDataRole.UserRole, p)

        # Docs
        self.table.setRowCount(0)
        for r, d in enumerate(reversed(self.documents)):
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(d.date))
            self.table.setItem(r, 1, QTableWidgetItem(d.profile))
            self.table.setItem(r, 2, QTableWidgetItem(d.sender))
            self.table.setItem(r, 3, QTableWidgetItem(d.filename))
            self.table.setItem(r, 4, QTableWidgetItem(d.path))
            self.table.item(r, 0).setData(Qt.ItemDataRole.UserRole, d.path)
        self._update_profile_delete_action_state()
        self._update_account_delete_action_state()

    def _update_profile_delete_action_state(self, current=None, previous=None):
        item = current if current is not None else self.tree.currentItem()
        has_profile = isinstance(
            item.data(0, Qt.ItemDataRole.UserRole) if item else None,
            SearchProfile,
        )
        self.btn_delete_profile.setEnabled(has_profile)
        if has_profile:
            self.btn_delete_profile.setToolTip("Ausgewähltes Suchprofil löschen")
            self.btn_delete_profile.setAccessibleDescription("Löscht das aktuell ausgewählte Suchprofil.")
        else:
            self.btn_delete_profile.setToolTip("Wählen Sie zuerst ein Suchprofil aus.")
            self.btn_delete_profile.setAccessibleDescription("Deaktiviert, bis ein Suchprofil ausgewählt ist.")

    def _update_account_delete_action_state(self):
        has_account = self.list_acc.currentRow() >= 0
        self.btn_delete_account.setEnabled(has_account)
        if has_account:
            self.btn_delete_account.setToolTip("Ausgewählten IMAP-Account löschen")
            self.btn_delete_account.setAccessibleDescription("Löscht den aktuell ausgewählten IMAP-Account.")
        else:
            self.btn_delete_account.setToolTip("Wählen Sie zuerst einen IMAP-Account aus.")
            self.btn_delete_account.setAccessibleDescription("Deaktiviert, bis ein IMAP-Account ausgewählt ist.")

    # Actions
    def add_acc(self):
        d = AccountDialog(parent=self)
        if d.exec():
            a, pw = d.get_data(); self.accounts.append(a)
            if KEYRING_AVAIL and pw: keyring.set_password(APP_NAME, a.name, pw)
            self.save_config(); self.refresh_ui()

    def del_acc(self):
        r = self.list_acc.currentRow()
        if r >= 0: self.accounts.pop(r); self.save_config(); self.refresh_ui()

    def add_prof(self):
        if not self.accounts: QMessageBox.warning(self, UI_WARN_NO_ACCOUNT_TITLE, UI_WARN_NO_ACCOUNT_MSG); return
        d = ProfileDialog(self.accounts, global_settings=self.global_settings, parent=self)
        if d.exec(): self.profiles.append(d.get_profile()); self.save_config(); self.refresh_ui()

    def edit_prof(self, item, col):
        p = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(p, SearchProfile):
            d = ProfileDialog(self.accounts, p, self.global_settings, self)
            if d.exec():
                self.profiles[self.profiles.index(p)] = d.get_profile()
                self.save_config(); self.refresh_ui()

    def del_prof(self):
        item = self.tree.currentItem()
        if not item: return
        p = item.data(0, Qt.ItemDataRole.UserRole)
        if isinstance(p, SearchProfile): self.profiles.remove(p); self.save_config(); self.refresh_ui()

    def _sync_profile_order(self):
        """Liest die aktuelle Reihenfolge und Gruppenstruktur aus dem Tree
        und synchronisiert self.profiles entsprechend. Wird nach Drag&Drop
        aufgerufen (rowsMoved-Signal). Gruppe wird aus dem Top-Level-Item
        übernommen, sodass Moves zwischen Gruppen das Profil umnbenennen.
        """
        new_order = []
        for i in range(self.tree.topLevelItemCount()):
            group_item = self.tree.topLevelItem(i)
            # Gruppen-Namen bereinigen: "📁 Allgemein" -> "Allgemein"
            group_name = group_item.text(0).lstrip("📁 ").strip()
            for j in range(group_item.childCount()):
                child = group_item.child(j)
                profile = child.data(0, Qt.ItemDataRole.UserRole)
                if isinstance(profile, SearchProfile):
                    # Gruppe aktualisieren falls Profil in andere Gruppe gezogen wurde
                    profile.group = group_name
                    new_order.append(profile)
        self.profiles = new_order
        self.save_config()

    def run_all(self):
        if self.worker and self.worker.isRunning(): return

        # Calc Date
        t = self.cb_time.currentText()
        dt = None
        today = date.today()
        if t == "Ab diesem Jahr": dt = datetime(today.year, 1, 1)
        elif t == "Ab letztem Jahr": dt = datetime(today.year-1, 1, 1)
        elif t == "Ab letztem Monat": dt = datetime.now() - timedelta(days=30)

        self.btn_start.setText(UI_BTN_RUNNING); self.btn_start.setEnabled(False)
        self.log.clear()

        self.worker = GrabberWorker(self.profiles, self.accounts, self.global_settings, Path(self.base_path), self.documents, dt)
        self.worker.log.connect(self.log.appendPlainText)
        self.worker.finished.connect(self.on_finished)
        self.worker.start()

    def on_finished(self):
        self.btn_start.setText(UI_BTN_START); self.btn_start.setEnabled(True)
        self.save_config(); self.refresh_ui()

    def open_doc(self, r, c):
        p = self.table.item(r, 0).data(Qt.ItemDataRole.UserRole)
        if p: QDesktopServices.openUrl(QUrl.fromLocalFile(p))

    def brws(self):
        d = QFileDialog.getExistingDirectory(self, "Ziel", self.base_path)
        if d: self.ip_path.setText(d)

    def save_glob(self):
        self.base_path = self.ip_path.text()
        self.global_settings.download_attachments = self.ck_att.isChecked()
        self.global_settings.convert_body_to_pdf = self.ck_pdf.isChecked()
        self.global_settings.enable_hash_check = self.ck_hash.isChecked()
        self.global_settings.formats = [x.strip() for x in self.ip_fmt.text().split(",") if x.strip()]
        self.save_config()

    def export_redacted_library(self, output_path: Path) -> dict:
        payload = build_library_export_payload(
            self.profiles,
            self.accounts,
            self.documents,
            self.global_settings,
            Path(self.base_path),
            scheduler_interval=self.scheduler_interval,
        )
        write_library_export(output_path, payload)
        return payload

    def save_library_export(self):
        suggested_path = Path(self.base_path) / "docsgrabber-library-v1.json"
        selected_path, _ = QFileDialog.getSaveFileName(
            self,
            "Redigierten Export speichern",
            str(suggested_path),
            "JSON (*.json)",
        )
        if not selected_path:
            return
        try:
            payload = self.export_redacted_library(Path(selected_path))
            self.log.appendPlainText(
                f"[Export] Redigierter Companion-Export gespeichert: {selected_path}"
            )
            QMessageBox.information(
                self,
                UI_EXPORT_SUCCESS_TITLE,
                (
                    f"Redigierter Export gespeichert:\n{selected_path}\n\n"
                    f"Profile: {payload['run_summary']['exported_profile_count']}, "
                    f"Dokumente: {payload['run_summary']['exported_document_count']}"
                ),
            )
        except Exception as exc:
            logger.exception("save_library_export failed")
            QMessageBox.critical(
                self,
                UI_EXPORT_ERROR_TITLE,
                f"Redigierter Export konnte nicht gespeichert werden:\n{exc}",
            )

    # ==================== SCHEDULER ====================

    def _save_scheduler(self):
        """Speichert Scheduler-Einstellungen und (re)startet den Timer."""
        idx = self.cb_scheduler.currentIndex()
        self.scheduler_interval = SCHEDULER_INTERVALS[idx]
        self.save_config()
        self._apply_scheduler()
        if self.scheduler_interval > 0:
            self.log.appendPlainText(
                f"[Scheduler] Aktiviert: alle {self.scheduler_interval} Minuten"
            )
        else:
            self.log.appendPlainText("[Scheduler] Deaktiviert")

    def _apply_scheduler(self):
        """Startet oder stoppt den QTimer basierend auf scheduler_interval."""
        self._scheduler_timer.stop()
        if self.scheduler_interval > 0:
            self._scheduler_timer.start(self.scheduler_interval * 60 * 1000)
            next_run = datetime.now() + timedelta(minutes=self.scheduler_interval)
            self.lbl_scheduler_status.setText(
                UI_SCHEDULER_ACTIVE.format(interval=self.scheduler_interval)
                + " | " + UI_SCHEDULER_NEXT.format(time=next_run.strftime("%H:%M"))
            )
            self.lbl_scheduler_status.setStyleSheet("color: #2ecc71; font-weight: bold;")
        else:
            self.lbl_scheduler_status.setText(UI_SCHEDULER_INACTIVE)
            self.lbl_scheduler_status.setStyleSheet("color: #888;")

    def _on_scheduler_tick(self):
        """Wird vom QTimer aufgerufen -- startet einen automatischen Scan."""
        if self.worker and self.worker.isRunning():
            self.log.appendPlainText(
                "[Scheduler] Scan übersprungen (vorheriger Scan läuft noch)"
            )
            return
        self.log.appendPlainText(
            f"[Scheduler] Automatischer Scan gestartet ({datetime.now().strftime('%H:%M:%S')})"
        )
        self.run_all()
        # Naechsten Tick anzeigen
        if self.scheduler_interval > 0:
            next_run = datetime.now() + timedelta(minutes=self.scheduler_interval)
            self.lbl_scheduler_status.setText(
                UI_SCHEDULER_ACTIVE.format(interval=self.scheduler_interval)
                + " | " + UI_SCHEDULER_NEXT.format(time=next_run.strftime("%H:%M"))
            )

    def closeEvent(self, event):
        """Stoppt laufenden Worker sauber bevor das Fenster geschlossen wird."""
        self._scheduler_timer.stop()
        if self.worker and self.worker.isRunning():
            self.worker.requestInterruption()
            self.worker.wait(3000)
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    icon = get_app_icon()
    if icon and not icon.isNull():
        app.setWindowIcon(icon)
    win = MainWindow()
    win.show()
    sys.exit(app.exec())
