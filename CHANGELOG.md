# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
- CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md (GitHub-Policy Compliance)
- CHANGELOG.md mit Versionshistorie
- Regressionstests für Body-zu-PDF-Fallback, Profil-Drag&Drop und Batch-Ausführung aktiver Profile

### Geändert / Changed
- process_email() in 3 Untermethoden aufgeteilt (_parse_email_metadata, _save_attachment, _convert_body_to_pdf)
- 6 verbleibende bare except-Blöcke durch spezifische Exceptions ersetzt
- README.md und README-DE.md mit Profil-Sortierung und Batch-Ausführung synchronisiert
- README.md und README-DE.md um lokale Datenschutz-Hinweise ergänzt
- CONTRIBUTING.md, SECURITY.md und CODE_OF_CONDUCT.md auf GitHub-Policy-Stand gebracht

### Behoben / Fixed
- Deutsche Kategorien und Scheduler-Log verwenden echte Umlaute
- Veraltete Template-Mailadresse aus dem Verhaltenskodex entfernt

## [1.1.0] - 2026-05-02
### Added
- Drag&Drop-Profil-Sortierung im Profil-Tree
- Gmail Query Builder Dialog für IMAP- und Gmail-Suchabfragen
- E-Mail-Body-zu-PDF-Konvertierung (HTML + Plaintext-Fallback via xhtml2pdf)
- gmail_query Feld in SearchProfile für gespeicherte Queries

## [1.0.0] - 2026-02-22

### Hinzugefügt / Added
- IMAP-Verbindung mit Multi-Account-Support
- Download von E-Mail-Anhängen (PDF, DOCX, XLSX, Bilder)
- Automatische PDF-Konvertierung (DOCX, XLSX, Bilder -> PDF)
- OCR-Erkennung für bildbasierte PDFs (Tesseract)
- Suchprofile mit Query-Builder
- Duplikat-Erkennung via SHA256-Hash
- PyQt6-GUI mit Dark Theme
- Fortschrittsanzeige für Downloads
- README.md mit vollständiger Dokumentation

### Geändert / Changed
- POPPLER_PATH konfigurierbar (Auto-Detect + Umgebungsvariable)
- sanitize_filename() mit Input-Validierung (None/Empty Check)
- Type Hints für Helper-Funktionen
- Docstrings für alle 4 Datenklassen
- Error Handling: Exceptions werden geloggt statt silent fail

### Behoben / Fixed
- APP_NAME Versionsinkonzistenz korrigiert (V7 -> V1)
- Bare except in calculate_file_hash() und decode_header_str()
