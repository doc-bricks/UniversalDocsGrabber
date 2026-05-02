# UniversalDocsGrabber V1

**Automatischer Download und Verwaltung von Dokumenten aus IMAP-E-Mails**

![Status](https://img.shields.io/badge/status-VALIDIERT%20%26%20BEREIT-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)

---

## Überblick

UniversalDocsGrabber ist eine PySide6-Desktop-Anwendung für den Download,
die Konvertierung und die Ablage von Dokumenten aus IMAP-Postfächern.

![UniversalDocsGrabber Screenshot](README/screenshots/main.png)

### Kernfunktionen

- Multi-Account IMAP Support
- Suchprofile mit Filtern für Absender, Betreff und Zeitraum
- Download von PDF, DOCX, DOC, JPG, PNG und weiteren Dokumenttypen
- Automatische Konvertierung nach PDF
- OCR für PDFs ohne Textebene
- Hash-basierte Duplikate-Erkennung
- Scheduler für wiederkehrende Scans
- Auto-Kategorisierung mit Standard- und benutzerdefinierten Regeln

---

## Installation

### Voraussetzungen

- Python 3.8+
- Windows für Word-Konvertierung via `win32com`
- Optional: Tesseract OCR
- Optional: Poppler

### Basis-Setup

```bash
pip install -r requirements.txt
```

### Optionale Komponenten

- `pytesseract` und `pdf2image` für OCR
- `pywin32` und `docx2pdf` für Word-zu-PDF unter Windows

### Poppler Installation

1. Download: <https://github.com/oschwartz10612/poppler-windows/releases>
2. Nach `C:\Program Files\poppler\` entpacken
3. Falls nötig `POPPLER_PATH` in `UniversalDocsGrabberV1.py` anpassen

### Tesseract Installation

1. Download: <https://github.com/UB-Mannheim/tesseract/wiki>
2. Nach `C:\Program Files\Tesseract-OCR\` installieren
3. Zum `PATH` hinzufügen

---

## Nutzung

### Start

```bash
python UniversalDocsGrabberV1.py
```

oder direkt:

```bash
START.bat
```

### Typischer Workflow

1. IMAP-Konto im Tab `🔑 Konten` anlegen
2. Suchprofil mit Gruppe, Filtern und Zielordner erstellen
3. Zeitfilter setzen
4. Scan über `🚀 START` auslösen
5. Dokumente im Tab `📂 Dokumente` durchsuchen

---

## Funktionen im Detail

### Suchprofile

- Gruppen für thematische Sortierung
- Profil-spezifische Override-Einstellungen
- Zeitfilter pro Lauf

### Konvertierung

- Word → PDF via `win32com` oder `docx2pdf`
- TXT → PDF via `reportlab`
- Bilder → PDF via Pillow
- OCR für PDFs ohne Textebene

### Scheduler & Auto-Kategorisierung

- Wiederkehrende Scans von 15 Minuten bis 24 Stunden
- Läufe werden übersprungen, wenn bereits ein anderer Scan aktiv ist
- Regelbasierte Auto-Kategorisierung für Rechnungen, Versand, Verträge,
  Kündigungen, Steuer, Versicherung, Bewerbungen und Bank

### Deduplizierung

- SHA-256 Hash-Check
- Optional pro Profil aktivierbar

---

## Projektstruktur

```text
RDY_UniversalDocsGrabber/
├── UniversalDocsGrabberV1.py
├── START.bat
├── UniversalDocsGrabber_icon.ico
├── requirements.txt
├── README.md
├── README/screenshots/main.png
└── releases/
```

### Lokale Konfigurationsdateien

- `%USERPROFILE%\.univ_docs_grabber\config_v1.json`
- `%USERPROFILE%\.univ_docs_grabber\documents.json`
- `%USERPROFILE%\Downloads\UnivDocs\`

---

## Bekannte Grenzen

- OCR benötigt Tesseract und Poppler
- Word-Konvertierung benötigt Windows-Komponenten
- Die Suche arbeitet bewusst konservativ mit begrenzter Mail-Menge pro Profil

---

## Status

- [x] Scheduler mit konfigurierbaren Intervallen
- [x] Auto-Kategorisierung
- [x] Hash-Deduplizierung
- [x] Profil-Gruppierung und Settings-Overrides
- [ ] Cloud-Sync ist aktuell bewusst nicht integriert

---

## Lizenz & Autor

- Lizenz: [MIT](LICENSE)
- Autor: Lukas Geiger
- GitHub: [github.com/lukisch](https://github.com/lukisch)

---

## English

### Overview

UniversalDocsGrabber is a PySide6 desktop application that downloads,
converts, and organizes documents from IMAP mailboxes.

### Highlights

- Multi-account IMAP support
- Search profiles with sender, subject, and date filters
- PDF conversion for documents, images, and text bodies
- OCR support for scanned PDFs
- SHA-256 duplicate detection
- Built-in scheduler for recurring scans
- Rule-based auto-categorization

### Quick Start

```bash
pip install -r requirements.txt
python UniversalDocsGrabberV1.py
```

### License

MIT License
