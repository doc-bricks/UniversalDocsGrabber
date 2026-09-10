# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Fixed
- Fixed transparent pixel artifact in Web/PWA companion `apple-touch-icon-180.png` ensuring 100% opaque RGB compliance for iOS home screen icons and passing all 32 Node smoke tests.
- Declared `"type": "module"` in `web_companion/package.json` to eliminate Node ESM loader warning.
- Ensured proper UTF-8 formatting and asset paths in `manifest.webmanifest` and updated pre-cache assets in `sw.js`.

### Added
- Added `.ruff_cache/`, `.gemini/`, and `.cursor/` to `.gitignore`.
- Added companion icon assets (`apple-touch-icon-180.png`, `apple-touch-icon.png`, `favicon.ico`, `favicon.png`, `icon-192.png`, `icon-512.png`, `icon.png`).

### Geändert / Changed
- Git status, remote synchronization & hygiene check (SOFTWARE_GITHUB) on 2026-09-10.
- Updated `llms.txt` with `Last-checked: 2026-09-10`.

## [1.1.4] - 2026-08-21

### Verification / Status
- 2026-08-21: Discoverability, README-Design, Badges, Quick Navigation, Mermaid Sequence Diagram, CI Matrix Modernization & Metadata Parity Test Suite (Pfad B). Clean 100% pass on 65 Pytest tests and 32 Web Companion Node tests (97 total contract tests).

### Added / Hinzugefügt
- Added interactive bilingual Mermaid Sequence Diagram for the end-to-end IMAP Document Ingestion, SHA-256 Deduplication, PDF Conversion & Redacted PWA Export lifecycle in `README.md` and `README-DE.md`
- Added structured Quick Navigation bar across key sections (Quick Start, Architecture, Lifecycle, Privacy & Security, Web Companion, Sibling Tools, Security Policy, LLM Context) in both READMEs
- Expanded CI workflow matrix in `.github/workflows/ci.yml` to Python 3.13 and Node.js 24.x
- Expanded PEP 621 metadata in `pyproject.toml` with Python 3.13, POSIX Linux, MacOS, OS Independent classifiers, and direct `Security` project URL
- Expanded Sibling Tools Ecosystem Matrix across `doc-bricks`, `file-bricks`, `dev-bricks`, `ellmos-ai`, and `open-bricks`

### Geändert / Changed
- Updated Shields.io badges in `README.md` and `README-DE.md` (CI Status, Security Policy, Python 3.8-3.13, Windows/macOS/Linux platforms, 97 passed contract tests, 100% Offline / Zero-Egress)
- Updated `llms.txt` with `Last-checked: 2026-08-21` and updated CI matrix specification
- Expanded automated metadata parity test suite in `tests/test_metadata.py` to cover PEP 621 classifiers, security URLs, Mermaid sequence diagrams, quick navigation, and CI matrix

## [1.1.4] - 2026-08-20

### Verification / Status
- 2026-08-20: Technical hygiene, CI hardening, and metadata parity check (Pfad A). Clean 100% pass on 63 Pytest tests and 32 Web Companion Node tests (95 total contract tests).

### Added / Hinzugefügt
- Added multi-OS (Ubuntu, Windows, macOS) and multi-version (Python 3.10, 3.11, 3.12, Node.js 18.x, 20.x, 22.x) GitHub Actions CI workflow in `.github/workflows/ci.yml`
- Added comprehensive automated metadata, manifest, security, CI, and ecosystem parity test suite in `tests/test_metadata.py`
- Expanded `SECURITY.md` to full bilingual standard with Local-First / Zero-Egress invariants, Windows Credential Vault safeguards, and confidential reporting via `security@ellmos.ai`
- Expanded sibling tools ecosystem matrix across `doc-bricks`, `file-bricks`, `dev-bricks`, and `open-bricks` in `README.md` and `README-DE.md`

### Geändert / Changed
- Bumped version to `1.1.4` across `pyproject.toml`, `llms.txt`, and documentation
- Updated pytest configuration in `pyproject.toml` to automatically collect `source_platform_smoke.py` alongside standard unit tests
- Updated `llms.txt`, `README.md`, and `README-DE.md` badges and verification status to 95 passed contract tests (2026-08-20)

## [1.1.3] - 2026-08-14

## [1.1.3] - 2026-07-27

### Geändert / Changed
- Discoverability-, SEO- & Marketing-Erstcheck (Pfad B) durchgeführt
- Aktualisierte `llms.txt` mit `Last-checked: 2026-07-27` und kombinierter Test-Verifizierung (83 bestandene Tests: 52 Pytest + 31 Web Companion)
- Aktualisierte Shields.io Status-Badges in `README.md` und `README-DE.md` zur Repräsentation der vollständigen Testsuite (83 passed)

## [1.1.2] - 2026-07-25

### Hinzugefügt / Added
- Standardisierte `pyproject.toml` (PEP 621) mit Paketmetadaten, Klassifikatoren, Schlüsselwörtern und Pytest-Konfiguration (`pythonpath = "."`)
- Shields.io Status-Badges (Pytest-Status, Lizenz, Plattform, Python, LLM-Ready, Datenschutz) in `README.md` und `README-DE.md`
- KI/LLM-Integrationshinweise (`> [!NOTE]`) für Agenten und automatisierte Audiot-Pipelines in `README.md` und `README-DE.md`
- Visualisierte Systemarchitektur & Datenflussdiagramme (Mermaid) in `README.md` und `README-DE.md`
- Aktualisierte `llms.txt` mit `Last-checked: 2026-07-25` und Verifizierungs-Status (52 passing Pytest-Tests)

## [1.1.0] - 2026-06-11

### Hinzugefügt / Added
- `build_exe.bat` für reproduzierbare lokale Windows-EXE-Builds außerhalb von
  OneDrive mit Build-venv und Build-Exclude-Scanner
- README-Suchbegriffe, Companion-Screenshot-Platz und Web/PWA-Metadaten für
  bessere GitHub- und Web-Auffindbarkeit
- `llms.txt` als maschinenlesbaren Projektkontext für Crawler und LLM-Tools
- Portierungsplan für Windows Desktop, macOS/Linux-Smokes und Web/PWA-Companion
- Geplantes redigiertes Austauschformat `docsgrabber-library-v1.json`
- Statischer Web/PWA-Companion unter `web_companion/` mit Import,
  Profil-/Kategorienübersicht, Dokumentsuche, Detailansicht, Demo-Export,
  Manifest, Service Worker und Node-Smokes
- Redigierter Desktop-Export `docsgrabber-library-v1.json` mit Account-Refs,
  Profilen, Kategorien, Dokumentmetadaten und Profilstatistiken
- Tests für Export-Payload und UTF-8-JSON ohne BOM
- Reproduzierbarer Source-Smoke `tests/source_platform_smoke.py` für
  Offscreen-Start, Config-Roundtrip, nicht-Windows-Word-Pfad und optionale
  OCR-Stacks
- GitHub-Workflow `.github/workflows/source-platform-smoke.yml` für
  `ubuntu-latest` und `macos-latest`
- Privacy-/Gitignore-Hinweise für lokale App-Daten in README.md und README-DE.md
- `.gitattributes` für stabile Zeilenenden im Repository
- CODE_OF_CONDUCT.md, CONTRIBUTING.md, SECURITY.md (GitHub-Policy Compliance)
- CHANGELOG.md mit Versionshistorie
- 15 pytest-Tests für `GrabberWorker._auto_categorize` (disabled-shortcut, custom rules nach Subject/Sender, custom > default, alle 8 Default-Kategorien: Rechnungen, Versand, Verträge, Kündigungen, Steuer, Versicherung, Bewerbungen, Bank, plus no-match)
- 12 statische + 1 Runtime-Tests für den Web/PWA-Companion (`web_companion/tests/pwa_smoke.test.mjs`)
- PWA-Icons (192/512 px, standard + maskable) in `web_companion/icons/`
- Regressionstests für Body-zu-PDF-Fallback, Profil-Drag&Drop und Batch-Ausführung aktiver Profile
- Regressionstests für Gmail-Raw-Suche mit IMAP-Fallback sowie klar beschriftete
  Navigation/Löschaktionen im UI

### Geändert / Changed
- `START.bat` startet bevorzugt eine frische lokale EXE und fällt erst danach
  auf den Python-Source-Start zurück
- README.md und README-DE.md dokumentieren den lokalen Windows-EXE-Build und
  den bevorzugten Startpfad
- `.gitignore` ignoriert jetzt `LOCK*.txt`, damit temporäre Projekt-Sperren
  nicht versehentlich im öffentlichen Repo landen
- README.md, README-DE.md und `llms.txt` um Startpunkte, Suchphrasen und
  Abgrenzung zu generischen Dokumentenviewern, RAG-Parsern, Cloud-OCR-Diensten
  und Dokumentationsgeneratoren ergänzt
- Community- und Security-Dateien von Template-Resten, Fake-Mail-Kontakt und veralteten Repo-URLs bereinigt
- Sichtbare deutsche Endnutzertexte auf echte Umlaute normalisiert
- process_email() in 3 Untermethoden aufgeteilt (_parse_email_metadata, _save_attachment, _convert_body_to_pdf)
- 6 verbleibende bare except-Blöcke durch spezifische Exceptions ersetzt
- README.md und README-DE.md mit Profil-Sortierung und Batch-Ausführung synchronisiert
- README.md und README-DE.md um lokale Datenschutz-Hinweise ergänzt
- CONTRIBUTING.md, SECURITY.md und CODE_OF_CONDUCT.md auf GitHub-Policy-Stand gebracht
- IMAP-Suche nutzt bei Gmail jetzt `X-GM-RAW` plus Standardfilter und fällt auf
  klassische IMAP-Kriterien zurück, wenn die Server-Erweiterung fehlt
- Tabs, Löschbuttons und Ordnerauswahl im UI tragen jetzt klare Beschriftungen,
  Tooltips und Accessible Names
- Einstellungen-Tab bietet jetzt einen Companion-Export-Button für den
  redigierten Plattform-Bridge-JSON-Export
- README, README-DE, `PORTIERUNGSPLAN.md`, `AUFGABEN.txt` und
  `web_companion/README.md` auf den umgesetzten Companion-Stand synchronisiert
- README, README-DE, `PORTIERUNGSPLAN.md` und `AUFGABEN.txt` auf den
  verifizierten macOS-/Linux-Source-Smoke-Stand synchronisiert

### Behoben / Fixed
- `UniversalDocsGrabberV1.py`: IMAP-Suche und Fetch nutzen jetzt UIDs statt
  Sequenznummern (MSN) — `conn.uid('search', ...)` / `conn.uid('fetch', ...)`
  statt `conn.search()` / `conn.fetch()`. Schützt vor MSN-Verschiebung durch
  parallele Expunge-Operationen anderer IMAP-Sessions (U4).
- `UniversalDocsGrabberV1.py`: NIL-Guards in `_convert_body_to_pdf()` —
  `get_payload(decode=True)` kann bei malformed Multipart-Teilen None zurückgeben;
  ohne Guard entstand `AttributeError: 'NoneType' has no attribute 'decode'` (U5).
- `UniversalDocsGrabberV1.py`: NIL-Guard in `process_email()` — nach
  `uid('fetch', ...)` kann `data[0]` None sein wenn die Nachricht zwischen Search
  und Fetch gelöscht wurde (U6).
- `UniversalDocsGrabberV1.py`: Sentinels (`pisa = None`,
  `pytesseract = SimpleNamespace(...)`, `PdfReader = None`, `PdfWriter = None`,
  `convert_from_path = None`) bei fehlendem Optionalpaket — ermöglicht
  Monkeypatching in Tests auch ohne installierte Abhängigkeiten (U7).
- `UniversalDocsGrabberV1.py`: Office-zu-PDF-Fallback entkoppelt; fehlendes
  `win32com` blockiert den vorhandenen `docx2pdf`-Pfad nicht mehr
- `web_companion/app.js`: `escHtml()` hinzugefügt und in allen `innerHTML`-Interpolationen (`renderProfiles`, `renderCategories`, `renderDocuments`, `renderDocumentDetail`) eingesetzt — XSS-Schutz für Library-Daten
- `web_companion/app.js`: `document`-Parameter-Shadowing in `renderDocuments`-forEach behoben (`doc` statt `document`), DOM-Global bleibt unberührt
- `web_companion/sw.js`: `self.skipWaiting()` im install-Handler, `self.clients.claim()` im activate-Handler und `ignoreSearch: true` in `caches.match()` für stabiles Offline-Verhalten ergänzt
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
