# UniversalDocsGrabber

Desktop tool for automatically downloading, converting, and organizing documents from IMAP mailboxes.

> **Deutsche Dokumentation:** [README-DE.md](README-DE.md)

![Status](https://img.shields.io/badge/status-released-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20desktop-lightgrey)

![UniversalDocsGrabber Screenshot](README/screenshots/main.png)

## Features

- Multi-account IMAP support
- Search profiles with sender, subject, and date filters
- Downloads PDF, DOCX, DOC, JPG, PNG, and other document types
- Automatic PDF conversion for documents, images, and text bodies
- OCR support for scanned PDFs via Tesseract
- SHA-256 hash-based duplicate detection
- Built-in scheduler for recurring scans from 15 minutes to 24 hours
- Rule-based auto-categorization for invoices, shipping, contracts, taxes, insurance, and related mail
- Drag-and-drop profile ordering and batch runs for all active profiles
- Gmail raw queries now combine with sender/subject/date filters on servers
  with `X-GM-RAW`; other IMAP servers fall back to classic
  `FROM`/`SUBJECT`/`SINCE` searches
- Local-first storage for account settings and indexed document metadata
- Redacted `docsgrabber-library-v1.json` export for a future Web/PWA companion
- Clearer tab/button labels and tooltips reduce ambiguity for destructive
  actions and download-path selection

## Privacy Model

UniversalDocsGrabber runs locally on your Windows machine. Mail credentials are stored through the operating system keyring when available, while project metadata is kept in the user profile. The application does not ship with telemetry, cloud sync, or a hosted backend.

## Installation

### Requirements

- Python 3.8+
- Windows for Word conversion via `win32com`
- Optional: Tesseract OCR
- Optional: Poppler

### Setup

```bash
pip install -r requirements.txt
```

### Optional: Poppler

1. Download from <https://github.com/oschwartz10612/poppler-windows/releases>
2. Extract to `C:\Program Files\poppler\`
3. Adjust `POPPLER_PATH` in `UniversalDocsGrabberV1.py` if needed

### Optional: Tesseract

1. Download from <https://github.com/UB-Mannheim/tesseract/wiki>
2. Install to `C:\Program Files\Tesseract-OCR\`
3. Add to `PATH`

## Run

```bash
python UniversalDocsGrabberV1.py
```

or double-click `START.bat`.

## Typical Workflow

1. Add an IMAP account in the `Accounts` tab
2. Create a search profile with group, filters, and target folder
3. Set a date range
4. Start a single profile or scan all active profiles with `START`
5. Browse results in the `Documents` tab
6. Use `Settings -> Companion-Export -> Redigierten Export speichern...` for a redacted library snapshot

## Features in Detail

### Search Profiles

- Group-based organization for thematic sorting
- Drag-and-drop sorting between groups
- Profile-specific override settings
- Per-run date filters

### Conversion

- Word to PDF via `win32com` or `docx2pdf`
- TXT to PDF via `reportlab`
- Images to PDF via Pillow
- OCR for PDFs without a text layer

### Scheduler & Auto-Categorization

- Recurring scans from 15 minutes to 24 hours
- Runs skipped if another scan is already active
- Batch execution processes all active profiles grouped by account
- Rule-based auto-categorization for invoices, shipping, contracts, cancellations, taxes, insurance, applications, and banking

### Deduplication

- SHA-256 hash check
- Configurable per profile

## Local Data

- `%USERPROFILE%\.univ_docs_grabber\config_v1.json`
- `%USERPROFILE%\.univ_docs_grabber\documents.json`
- `%USERPROFILE%\Downloads\UnivDocs\`

These files are intentionally ignored by Git because they can contain account names, local paths, document metadata, and downloaded documents.

## Known Limitations

- OCR requires Tesseract and Poppler
- Word conversion requires Windows components
- Search is intentionally conservative and limits the mail count per profile

## Platform Strategy

The Windows desktop app remains the full version for IMAP access, OCR,
conversion, scheduling, and local file storage. macOS and Linux are planned as
source smoke-test targets. Web, Android, and iOS should use a future PWA
companion based on a redacted `docsgrabber-library-v1.json` export instead of a
native mail-fetching clone.

The export contains profiles, categories, document metadata, profile statistics,
and redacted path hints, but no credentials, document bodies, or PDF contents.

See [PORTIERUNGSPLAN.md](PORTIERUNGSPLAN.md) and [EXPORTFORMAT.md](EXPORTFORMAT.md).

## Development

```bash
python -m pytest -q
python -m py_compile UniversalDocsGrabberV1.py
```

## Related Tools

Part of the [doc-bricks](https://github.com/doc-bricks) mail suite:

| Tool | Description |
|------|-------------|
| [MailProcessor](https://github.com/doc-bricks/MailProcessor) | System tray launcher for all Universal Mail Tools |
| [UniversalMailCleaner](https://github.com/doc-bricks/UniversalMailCleaner) | Rule-based IMAP mailbox cleaner with safe mode |
| [UniversalInvoiceMail](https://github.com/doc-bricks/UniversalInvoiceMail) | Extract invoices and receipts from IMAP mail |

## License

[MIT](LICENSE) - Lukas Geiger
