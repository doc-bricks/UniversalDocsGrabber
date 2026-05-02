# Changelog / Aenderungsprotokoll

Alle wesentlichen Aenderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [1.1.0] - 2026-05-02
### Added
- Drag&Drop Profil-Sortierung im Profil-Tree
- Gmail Query Builder Dialog für IMAP- und Gmail-Suchabfragen
- E-Mail-Body zu PDF Konvertierung (HTML + Plaintext-Fallback via xhtml2pdf)
- gmail_query Feld in SearchProfile für gespeicherte Queries

## [Unreleased]

### Hinzugefuegt / Added
- CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md (GitHub-Policy Compliance)
- CHANGELOG.md mit Versionshistorie

### Geaendert / Changed
- process_email() in 3 Untermethoden aufgeteilt (_parse_email_metadata, _save_attachment, _convert_body_to_pdf)
- 6 verbleibende bare except-Bloecke durch spezifische Exceptions ersetzt

## [1.0.0] - 2026-02-22

### Hinzugefuegt / Added
- IMAP-Verbindung mit Multi-Account-Support
- Download von E-Mail-Anhaengen (PDF, DOCX, XLSX, Bilder)
- Automatische PDF-Konvertierung (DOCX, XLSX, Bilder -> PDF)
- OCR-Erkennung fuer bildbasierte PDFs (Tesseract)
- Suchprofile mit Query-Builder
- Duplikat-Erkennung via SHA256-Hash
- PyQt6-GUI mit Dark Theme
- Fortschrittsanzeige fuer Downloads
- README.md mit vollstaendiger Dokumentation

### Geaendert / Changed
- POPPLER_PATH konfigurierbar (Auto-Detect + Umgebungsvariable)
- sanitize_filename() mit Input-Validierung (None/Empty Check)
- Type Hints fuer Helper-Funktionen
- Docstrings fuer alle 4 Datenklassen
- Error Handling: Exceptions werden geloggt statt silent fail

### Behoben / Fixed
- APP_NAME Versionsinkonzistenz korrigiert (V7 -> V1)
- Bare except in calculate_file_hash() und decode_header_str()
