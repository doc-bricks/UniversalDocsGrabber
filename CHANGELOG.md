# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Windows Store Readiness & Packaging Hardening (2026-09-23)
- **Windows Store Preflight & Tooling:** Implemented `scripts/run_windows_wack.py` supporting `--dry-run`, automated Windows SDK `appcert.exe` detection, admin privilege checking, and XML report parsing to JSON summaries.
- **WACK Preflight Validation:** Generated `releases/windowsstore/test_reports/wack_preflight_20260923.xml` and verified machine-readable summary `wack_preflight_20260923.json` (6 PASS, 0 FAIL, 0 WARNING).
- **Manifest Alignment:** Updated `store_package/UniversalDocsGrabber/AppxManifest.xml` `<Logo>` property to canonical `icons\StoreLogo.png`.
- **WACK Protocol:** Updated `releases/windowsstore/WACK_PROTOCOL.md` documenting preflight pass and execution commands.
- **Plan D Pointer:** Added `REPO.pointer.json` (`ellmos-repo-pointer-v1`) linking to `doc-bricks/UniversalDocsGrabber` and canonical checkout `C:\_Local_DEV\repos\UniversalDocsGrabber`.

### Verification / Status
- 2026-09-23: Windows Store Readiness Audit (Portfolio Check). 31/31 preflight checks passing, 102/102 Pytest contract tests passing, 32/32 Web Companion Node tests passing (134 total contract tests), zero ruff lint findings. WACK preflight 6 PASS / 0 FAIL.
- 2026-09-22: Pfad A Repository Hygiene, CI Lifecycle Workflows, PEP 621 Standard License Files, Multi-Host Lock Defense & Extended Contract Test Suite. Clean 100% pass on 102 Pytest tests and 32 Web Companion Node tests (134 total contract tests). Zero ruff lint findings over 5 rule sets (E, F, W, B, C4), zero Python compilation errors, zero git whitespace discrepancies. Version freeze strictly preserved per T-20260920-167562623.

### Added / Hinzugefügt
- Added canonical Open-Source `NOTICE` attribution file in repository root following open-bricks / doc-bricks ecosystem standards.
- Added `.github/workflows/welcome.yml` automated workflow using `actions/first-interaction@v3` with concurrency control, timeout guardrails, and friendly onboarding guidance for new contributors and issue reporters.
- Added concurrency control (`cancel-in-progress: true`) to `.github/workflows/stale.yml`.
- Standardized PEP 621 `license-files = ["LICENSE", "NOTICE", "THIRD_PARTY_LICENSES.md", "THIRD_PARTY_LICENSES.txt"]` and added `"Notice"` URL under `[project.urls]` in `pyproject.toml`.
- Enhanced `[tool.pytest.ini_options]` in `pyproject.toml` with `minversion = "7.0"` and `norecursedirs` to guard against unintended scanning of cache and virtualenv directories.
- Expanded multi-host conflict patterns (`*-ASUS*`, `*-LAPTOP*`, `*-Mac Studio*`, `*-MacBook*`), canonical lock defense (`LOCK.user.*`, `LOCK.until.*`, `LOCK.condition.*`, `.automation-lock`), and cache exclusions (`.hypothesis/`, `.turbo/`, `.nyc_output/`) in `.gitignore`.
- Re-audited `THIRD_PARTY_LICENSES.md` for 2026-09-22 confirming 100% permissive runtime dependencies, unprivileged `RunAsInvoker` security boundary, zero cloud egress, and LGPL-3.0 dynamic linking transparency.
- Added 4 new automated contract tests in `tests/test_metadata.py` (`test_notice_attribution_file_present_and_compliant`, `test_welcome_workflow_present_and_configured`, `test_pyproject_pep621_license_files_and_notice_url`, `test_changelog_unreleased_pfad_a_entry_present`).

## [1.1.7] - 2026-09-14 (Updated 2026-09-18: Store Readiness Staging)

### Store Readiness & Packaging Staging (2026-09-18)
- **Store-Readiness Preflight & Packaging Staging:** Implemented comprehensive MSIX Desktop-Bridge packaging staging under `releases/windowsstore/` (`BUILD.md`, `WACK_PROTOCOL.md`, `store_settings.json`, `store_listing_de.md`, `store_listing_en.md`, `StoreLogo.png`).
- **MSIX Manifest:** Created valid `store_package/UniversalDocsGrabber/AppxManifest.xml` with `runFullTrust` and `internetClient` capabilities, targeted device family Windows 10/11, and proper `uap:VisualElements` hierarchy.
- **Store Tile Assets & 1080p Screenshots:** Added automated asset generator `scripts/generate_store_assets.py` creating complete tile sets (44x44, 50x50, 150x150, 310x150, 310x310) in `store_assets/` and `store_package/UniversalDocsGrabber/assets/` plus 4 professional 1920x1080 store screenshots in `screenshots/store/` and `releases/windowsstore/screenshots/`.
- **Preflight Checker & Contract Testsuite:** Extended `scripts/check_store_readiness.py` to 31 automated validations and added comprehensive pytest contract suite `tests/test_store_materials.py` (11 contract tests). 100% green across 98 pytest tests.

### Verification / Status
- 2026-09-14: Pfad B Discoverability, Visual Architecture, 16-Point Navigation Parity, Direct 10-Dimension Comparative Matrix, Enriched Target Personas & Extended Contract Test Suite. Clean 100% pass on 78 Pytest tests and 32 Web Companion Node tests (110 total contract tests). Zero ruff lint findings over 5 rule sets (E, F, W, B, C4), zero Python compilation errors, and zero git whitespace discrepancies.

### Added / Hinzugefügt
- Integrated full **10-dimension Comparative Matrix table directly** into `README.md` and `README-DE.md`, providing instant evaluation vs. Cloud SaaS (DocuWare/Dext), Heavy Self-Hosted DMS (Paperless-ngx), Traditional Mail Clients (Thunderbird/Outlook), and Ad-Hoc Scripts across 10 critical operational dimensions.
- Expanded quick navigation to a **16-point bilingual table** with 100% reciprocal anchor parity between English (`#comparative-matrix-vs-alternatives`) and German (`#vergleichsmatrix-gegenüber-alternativen`).
- Deepened **Target Personas & Discoverability** section with structured profiles, acute pain points, and concrete solutions for Solo Entrepreneurs & Small Business Bookkeepers, Legal & Compliance Assistants, Privacy-Conscious Power Users, and Local-First AI/Automation Engineers.
- Added 2 new contract tests in `tests/test_metadata.py` (`test_comparative_matrix_parity` and `test_target_personas_structure_and_parity`) extending total contract tests from 108 to 110.

### Geändert / Changed
- Bumped project version to `1.1.7` across `pyproject.toml`, `store_package.json`, `WINDOWS_STORE_PREP.md`, `README.md`, `README-DE.md`, `llms.txt`, and contract test assertions.
- Updated Shields.io badges and documentation readbacks to 110 passed contract tests and currency date `2026-09-14`.
- Synchronized `THIRD_PARTY_LICENSES.md` audit verification date and `MARKETING-LOG.txt` revision history.

## [1.1.6] - 2026-09-12

### Verification / Status
- 2026-09-12: Pfad A Repository Hygiene, CI Matrix & Concurrency Hardening, PEP 621 Metadata Expansion & Contract Test Suite Extension. Clean 100% pass on 76 Pytest tests and 32 Web Companion Node tests (108 total contract tests). Zero ruff lint errors over 5 rule sets (E, F, W, B, C4), zero compile errors, and zero git whitespace discrepancies.

### Added / Hinzugefügt
- Added GitHub Actions workflow concurrency control (`cancel-in-progress: true`) and job run-away timeout guardrails (`timeout-minutes: 15` on pytest/smoke, `timeout-minutes: 10` on node-pwa) in `.github/workflows/ci.yml` and `.github/workflows/source-platform-smoke.yml`.
- Added automated issue and pull request lifecycle workflow `.github/workflows/stale.yml` using `actions/stale@v9` with least-privilege permissions and exempt label filters.
- Added comprehensive multi-host cloud-sync conflict patterns (`* (kopie)*`, `*-WORKSTATION*`, `*-ASUS-GEI*`), canonical lock defense (`LOCK`, `LOCK.*`, `uv.lock`, `!package-lock.json`), and coverage cache filters to `.gitignore`.
- Expanded automated contract test suite in `tests/test_metadata.py` with 4 new contract tests: `test_ci_concurrency_and_timeout_guardrails`, `test_ci_stale_workflow_present`, `test_gitignore_multihost_and_lock_defense`, and `test_ruff_linter_configuration_and_clean_run` (now 76 Pytest + 32 Node = 108 contract tests).

### Geändert / Changed
- Bumped project version to `1.1.6` across `pyproject.toml`, `README.md`, `README-DE.md`, `llms.txt`, and `tests/test_metadata.py`.
- Expanded Ruff linting rule sets to `["E", "F", "W", "B", "C4"]` in `pyproject.toml` with zero findings across the entire codebase.
- Synchronized Shields.io badges and readback metrics in `README.md` and `README-DE.md` to version 1.1.6 and 108 passed contract tests.
- Updated `llms.txt` and `MARKETING-LOG.txt` with current verification metrics and hygiene audit trail.

## [1.1.5] - 2026-09-11

### Verification / Status
- 2026-09-11: Pfad B Fleet Parity Overhaul (Discoverability, Visual Architecture, Licensing Audit & Contract Parity) & Windows Store Readiness. Clean 100% pass on 72 Pytest tests and 32 Web Companion Node tests (104 total contract tests). Zero ruff lint errors, zero compile errors, and zero git whitespace discrepancies.

### Fixed
- Fixed multi-attachment collision bug in `UniversalDocsGrabberV1.py` where subsequent attachments of the same file extension within a single email were silently dropped due to identical base name collision; added indexed naming fallback (`_ATT_{index}_{name}.{ext}`).
- Fixed MIME attachment parsing to reliably detect attachments even when `Content-Disposition` is omitted or set inline by mailers, relying on `part.get_filename()`.
- Fixed transparent pixel artifact in Web/PWA companion `apple-touch-icon-180.png` ensuring 100% opaque RGB compliance for iOS home screen icons and passing all 32 Node smoke tests.
- Declared `"type": "module"` in `web_companion/package.json` to eliminate Node ESM loader warning.
- Ensured proper UTF-8 formatting and asset paths in `manifest.webmanifest` and updated pre-cache assets in `sw.js`.

### Added / Hinzugefügt
- Added standardized `THIRD_PARTY_LICENSES.md` open-source compliance inventory (Stand: 2026-09-11) verifying 100% permissive runtime dependencies (MIT, BSD, Apache, PSF) and LGPL-3.0 dynamic linking transparency (PySide6) with user replacement freedom and zero cloud egress.
- Added repository-level `MARKETING-LOG.txt` detailing 4 target personas (Bookkeepers, Legal/Compliance, Archivists, AI Engineers), bilingual high-intent keywords, 4-way competitive matrix, 16+ sibling tools ecosystem mapping, and 10 governance & runtime invariants (`INV-LOCAL-01` to `INV-SLA-10`).
- Completed Windows Store Release Readiness evaluation (`TW-UDG-01` / TASKPLAN #1151): added `store_package.json` manifest, `STORE_LISTING.md` (DE/EN with strict 10.1.3 keyword compliance), `PRIVACY.md`, `SUPPORT.md`, `WINDOWS_STORE_PREP.md`, automated preflight validator `scripts/check_store_readiness.py`, and contract test `tests/test_store_readiness.py`.
- Added multi-attachment and MIME attachment unit test suite in `tests/test_attachment_handling.py`.
- Added companion icon assets (`apple-touch-icon-180.png`, `apple-touch-icon.png`, `favicon.ico`, `favicon.png`, `icon-192.png`, `icon-512.png`, `icon.png`).
- Expanded Quick Navigation bar in `README.md` and `README-DE.md` to 15 key points with 100% mutual anchor parity.
- Added formal Governance & Runtime Invariants table to both READMEs.
- Added dedicated `Third-Party Licenses & Transparency` and `Marketing & Target Personas` sections to `README.md` and `README-DE.md`.
- Added strict Vulnerability Management SLAs (48h acknowledgment, 5 business days triage) and umbrella contact points (`security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`, `lukas@open-bricks.org`) in `SECURITY.md`.
- Expanded PEP 621 metadata in `pyproject.toml` with `Third-Party Licenses`, `Marketing Log`, `LLM Ready`, `Parent Organization`, and `Umbrella Ecosystem` URLs, plus `addopts = "-ra -v"` for pytest.

### Geändert / Changed
- Bumped version to `1.1.5` across `pyproject.toml`, `llms.txt`, and metadata contract test suites.
- Modernized Shields.io badges in `README.md` and `README-DE.md` (Version 1.1.5, Contract Tests passed, License MIT, Python 3.8-3.13, Platform Windows|macOS|Linux, Privacy Zero-Egress, Security Keyring, Security SLA 48h / 5d triage, Third-Party Audited 100% permissive, Marketing Log active, doc-bricks, open-bricks, LLM-Ready llms.txt, Last-checked 2026--09--11).
- Updated `llms.txt` to `Last-checked: 2026-09-11`, version 1.1.5, passed tests, and 10 invariants.
- Expanded automated contract test suite in `tests/test_metadata.py` with tests for 15-point navigation anchors, governance invariants, PEP 621 extended URLs, and licensing inventory.

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
