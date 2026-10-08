# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### WCAG 2.1 AA / BITV 2.0 Tastatur-Ergonomie, Menüleiste, Statusleiste & Barrierefreiheit (2026-10-09)
- **Barrierefreie Menüleiste (`QMenuBar`) & Globale Tastaturkürzel (`UniversalDocsGrabberV1.py`):**
  - Menüs mit Mnemonics und Tastaturkürzeln: `&Datei` (Alt+D: Zielordner öffnen Ctrl+O, Export Ctrl+E, Beenden Ctrl+Q), `&Bearbeiten` (Alt+B: Neues Profil Ctrl+N, Profil bearbeiten F2, Profil löschen Entf, Neues Konto Ctrl+Shift+A, Konto löschen Ctrl+Entf, Einstellungen speichern Ctrl+S), `&Aktionen` (Alt+K: Alle Profile starten Ctrl+R / F5), `&Ansicht` (Alt+A: Konten Ctrl+1, Dokumente Ctrl+2, Einstellungen Ctrl+3, Protokoll Ctrl+4), `&Sprache` (Alt+S: 6 Sprachen), `&Hilfe` (Alt+H: Tastaturkürzel F1, Über Shift+F1).
  - Dynamische Synchronisation der Menü-Aktionen mit Selektionsstatus und Account-Identity-Guard.
- **Barrierefreier Tastaturkürzel- & Accessibility-Dialog (`show_shortcuts_dialog`):**
  - Modaler, tastaturfreundlicher F1-Dialog mit strukturierter, nach Kategorien gruppierter Übersicht aller Tastaturkürzel.
  - Ausdrücklicher Hinweis auf WCAG 2.1 AA und BITV 2.0 Konformität.
  - Schließen-Button mit Standardfokus (`setDefault(True)`) für nahtlose Esc- und Enter-Bedienung; Headless-Bypass für Offscreen-CI/CD.
- **Barrierefreier Über-Dialog (`show_about_dialog`):**
  - Modaler Shift+F1-Dialog mit Versions-, Lizenz- (MIT) und Maintainer-Angaben.
- **Statusleiste (`QStatusBar`) & Screenreader-Feedback:**
  - Barrierefreie Statusleiste (`ACC_STATUSBAR`) mit dynamischem Status ("Bereit", "Suchlauf aktiv...", "Suchlauf abgeschlossen").
  - Permanente Zähler für konfigurierte Profile und gefundene Dokumente.
  - Live-Feedback beim Kopieren von Dateipfaden in die Zwischenablage.
- **Tastatur-Ergonomie in Tabellen und Bäumen:**
  - `AccessibleDocumentTable`: Enter öffnet das ausgewählte Dokument (`open_doc`); Ctrl+C kopiert den Dateipfad in die Zwischenablage mit Bestätigungsmeldung.
  - `AccessibleProfileTree`: Enter öffnet das ausgewählte Profil im Bearbeitungsdialog; Entf löscht das ausgewählte Profil.
  - `AccessibleAccountTable`: Entf löscht das ausgewählte Konto.
  - Formular-Ergonomie: Zugängliche Namen (`setAccessibleName`) und Tooltips für alle Eingabefelder in `AccountDialog` und `ProfileDialog`.
- **Lokalisierung (Policy P-006 Tier-2 6-Sprachen-Parität):**
  - 45 neue Lokalisierungsschlüssel für Menüs, Aktionen, Shortcuts, Dialoge und Statusleiste in `locales/translations.json`.
  - 100% Parität über alle 6 Sprachen (Deutsch, Englisch, Spanisch, Chinesisch, Japanisch, Russisch) mit echten deutschen Umlauten (`ä`, `ö`, `ü`, `Ä`, `Ö`, `Ü`, `ß`).
- **Automatisierte Barrierefreiheits-Vertragstests (`tests/test_ui_accessibility.py`):**
  - 9 neue hermetische Tests zur Verifikation von Menüleiste, F1-Dialog, Über-Dialog, Statusleiste, Tabellen-Tastaturnavigation, Dialog-Attributen, Sprachwechsel-Retranslation und Menü-Synchronisation (9/9 passed, 210 Tests gesamt 100% grün).

### Headless CLI Pipeline, DOS-Gerätenamen-Schutz & Export-Resilienz (2026-10-03)
- **Korrektur Account-Referenz-Fallback (`build_account_ref` in `cli.py` & `UniversalDocsGrabberV1.py`):**
  - Behebt Fehlverhalten, bei dem leere oder `None`-Accountnamen aufgrund des SHA-256-Hashes von leeren Bytes fälschlicherweise als `account-e3b0c44298fc` maskiert wurden; gibt nun deterministisch `account-unknown` zurück.
- **DOS/Windows-Gerätenamen & Stem-Sanitization (`sanitize_filename` in `cli.py` & `UniversalDocsGrabberV1.py`):**
  - Absicherung gegen reservierte Windows-Gerätenamen (`CON`, `PRN`, `AUX`, `NUL`, `CLOCK$`, `COM1`..`COM9`, `LPT1`..`LPT9`) auch bei vorhandener Dateiendung (z. B. `CON.pdf`, `nul.txt` -> `file_CON.pdf`, `file_nul.txt`).
- **Resiliente CLI-Dokumentfilterung & CSV-Export (`cli.py`):**
  - Defensive `None`-Behandlung bei `profile`, `path`, `date`, `sender` und `subject` in `--list-documents` und `export_documents_to_csv` verhindert `AttributeError: 'NoneType' object has no attribute 'lower'` und `TypeError`.
  - Keine fehlerhaften String-Konvertierungen `"None"` in exportierten CSV-Zellen; saubere Repräsentation als Leerstring.
- **Zielverzeichnis-Auflösung & atomare Schreiboperationen (`cli.py` & `UniversalDocsGrabberV1.py`):**
  - `--export-library` und `--export-csv` unterstützen nun direkte Zielverzeichnisse (automatisches Anhängen von `docsgrabber-library-v1.json` bzw. `documents_export.csv`) und leere Pfade ohne `PermissionError`/`IsADirectoryError`.
  - Atomare Schreibvorgänge via temporärer Zwischendatei (`.tmp`) und `os.replace` schützen vor beschädigten oder unvollständigen Exportdateien bei Prozessabbrüchen.
- **Konfigurations-Ladefluss & Diagnose-Hygiene (`load_data` & `check_system_stack` in `cli.py`):**
  - Defensive Fallbacks bei fehlendem oder ungültigem `base_path` und nicht-ganzzahligem `scheduler_interval`.
  - Sichere Bereinigung temporärer Schreibtestdateien im `finally`-Block bei der Stack-Diagnose.
- **Hermetische Regressionstests (`tests/test_bugsweep_cli_and_export_resilience_20261003.py`):**
  - 10 neue automatisierte Tests zur Absicherung aller Fehlerbehebungen (10/10 passed, 181 Tests gesamt 100% grün).

### Tier-2 6-Languages I18N Expansion (DE, EN, ES, ZH, JA, RU), Translator Engine & Parity Tooling (2026-10-02)
- **Mehrsprachiges Übersetzungssystem (`translator.py`):**
  - Implementierung von `TranslationSystem` v2.0 mit Unterstützung für 6 Sprachen: Deutsch (`de`), Englisch (`en`), Spanisch (`es`), Chinesisch (`zh`), Japanisch (`ja`), Russisch (`ru`).
  - 4-stufige deterministische Fallback-Kette: `target -> en -> de -> key` zur Vermeidung fehlender Übersetzungen.
  - Globale Hilfsfunktionen `t(key, **kwargs)`, `get_translator()` und `set_language(lang)`.
  - Automatische Systemerkennung via `detect_system_language()` (`locale.getdefaultlocale()`).
- **Lokalisierungskatalog (`locales/translations.json`):**
  - 162 standardisierte UI-, Menü-, Tab-, Tooltip-, Dialog-, Tabellen- und Barrierefreiheits-Schlüssel.
  - 100% Schlüsselparität über alle 6 Sprachen hinweg (insgesamt 972 Übersetzungs-Strings, 0 fehlende Schlüssel).
  - Authentische deutsche Umlaute (`ä`, `ö`, `ü`, `Ä`, `Ö`, `Ü`, `ß`) und spanische Akzente ohne ASCII-Kompensate.
- **CI / Paritäts-Validierungstool (`manage_translations.py`):**
  - CLI-Tool mit `--check` (Exit-Code 0 bei 100% Parität) und `--stats` für kontinuierliche Qualitätssicherung.
- **GUI-Integration (`UniversalDocsGrabberV1.py`):**
  - Neuer Sprachwähler (`QComboBox`) im Tab "Einstellungen".
  - Persistierung der Sprachauswahl in `config_v1.json` mit Rückwärtskompatibilität (Standard: `de`).
  - Live-UI-Neuübersetzung ohne Anwendungsneustart über `retranslate_ui()`.
- **Spanische Gesamtdokumentation (`README_es.md`):**
  - Vollständige spanische Übersetzung mit 1:1 struktureller Parität zu `README.md` und `README-DE.md` (18 nummerierte Abschnitte, reziproke HTML-Anker `sec-01` bis `sec-18`, 4 Personas, 5-Wege-Vergleichsmatrix, ASCII-Topologieprojektion, Mermaid-Diagramme, § 521 BGB Hinweis).
  - Dreisprachige Sprachleiste (`[English](README.md) | [Deutsch](README-DE.md) | [Español](README_es.md)`) in allen READMEs.
- **Automatisierte Vertragstests (`tests/test_i18n.py`):**
  - 12 hermetische Contract-Tests zur Validierung von Parität, Fallback-Kette, Umlauterhalt, Formatierung und Schema-Integrität.

### Pfad A Repository Hygiene, CI Lifecycle Workflows, Bilingual CONTRIBUTING & Contract Test Suite (2026-10-01)
- **CI Lifecycle Workflows (`.github/workflows/`):**
  - `.github/workflows/auto-assign.yml`: Automatisierte Zuweisung neu geöffneter Pull Requests an den Repo-Owner (`actions/github-script@v7`, `timeout-minutes: 5`, Concurrency `cancel-in-progress: true`, least-privilege `pull-requests: write`, `issues: write`).
  - `.github/workflows/label-sync.yml`: Automatisierter GitHub-Label-Abgleich via `workflow_dispatch` (`EndBug/label-sync@v2`, `timeout-minutes: 5`, Concurrency `cancel-in-progress: true`, least-privilege `issues: write`).
- **Kanonische GitHub Labels (`.github/labels.yml`):** Bereitstellung der 13 standardisierten Flotten-Labels gemäß `GOVERNANCE.md` §4.2 (`bug`, `enhancement`, `good first issue`, `help wanted`, `documentation`, `duplicate`, `wontfix`, `priority: high`, `priority: low`, `needs-triage`, `stale`, `security`, `dependencies`).
- **Zweisprachige CONTRIBUTING.md Guidelines:** Vollständig zweisprachiger Leitfaden (Deutsch & Englisch) mit expliziten Quality Gates (`pytest -ra -v`, `ruff check .`, `compileall`, `git diff --check`, `git diff -G"version = "`), Plan D Local Development Workflow (`C:\_Local_DEV\repos\UniversalDocsGrabber`), unprivilegierter `RunAsInvoker`-Nicht-Erhöhungsgarantie (`INV-SEC-02`), allen 10 Invarianten (`INV-LOCAL-01` bis `INV-PAR-10`) und verbindlicher Version-Freeze-Disziplin.
- **Level 1 SBOM Stand 2026-10-01 Re-Audit:**
  - `THIRD_PARTY_LICENSES.txt`: Plain-Text-Begleitdatei auf Stand `2026-10-01` aktualisiert; Invarianten-Matrix `INV-LOCAL-01`..`INV-SLA-10`, `RunAsInvoker` Non-Elevation, Zero-Copyleft Isolation, Volltextlizenzen (MIT, BSD-3, Apache-2.0, PSF) und § 521 BGB Gefälligkeitsrecht-Hinweis re-auditiert.
  - `THIRD_PARTY_LICENSES.md`: Audit-Datum auf `2026-10-01` harmonisiert.
- **Multi-Host Cloud-Sync Defense in `.gitignore`:** Ergänzung von `*-IDEAPAD*`, `*-IDEAPAD-GEI*`, `*-IDEAPAD-GEI.*` zur Absicherung gegen temporäre Host-Dateien.
- **PEP 621 Standardisierung in `pyproject.toml`:** Härtung von `norecursedirs` um `.pytest_tmp*`, `.tox`, `.hypothesis`, `.turbo`, `.nyc_output`.
- **Badges & Metadaten-Synchronisation:** Badges in `README.md` und `README-DE.md` auf `Verified-2026--10--01` / `Geprüft-2026--10--01` und `Last-checked-2026--10--01` / `Letzte-Prüfung-2026--10--01` synchronisiert; `llms.txt` aktualisiert.
- **Automatisierte Vertragstests:** Neue Contract-Tests in `tests/test_metadata.py` für CI-Lifecycle-Workflows, labels.yml, zweisprachige CONTRIBUTING Guidelines, SBOM Recency 2026-10-01 und Multi-Host-Tokens.
- **Strikte Versions-Freeze-Disziplin:** Version `1.1.7` per T-20260920-167562623 unverändert beibehalten.

### Pfad B Visual Architecture, ASCII 4-View Topology & Level 1 SBOM Text Companion (2026-09-30)
- **ASCII Four-View Architectural Topology:** Section 2 in `README.md` und `README-DE.md` um die kanonische 4-Ansichten-Architekturprojektion ([VIEW 1: CLIENT RUNTIMES, USER INTERFACES & AUTOMATION DRIVERS], [VIEW 2: UNIVERSALDOCSGRABBER SOVEREIGN CORE ENGINE & PIPELINE ORCHESTRATOR], [VIEW 3: RUNTIME PERSISTENCE, LOCAL DOCUMENT VAULT & SANITIZED EXPORTS], [VIEW 4: AIR-GAP DEFENSE PERIMETER, ZERO-EGRESS & GOVERNANCE]; deutsche Fassung [SICHT 1] bis [SICHT 4]) erweitert.
- **Level 1 SBOM Plain-Text Companion (`THIRD_PARTY_LICENSES.txt`):** Stand auf `2026-09-30` aktualisiert; Abschnitt 8 mit vollständiger Invarianten-Kreuzreferenzmatrix (`INV-LOCAL-01` bis `INV-SLA-10`), unprivilegierter `RunAsInvoker`-Nicht-Erhöhungszertifizierung (`INV-SEC-02`), Zero-Copyleft-Isolationsgarantie (`INV-LIC-08`) und gesetzlichem Hinweis (§ 521 BGB) integriert.
- **Level 1 SBOM Re-Audit (`THIRD_PARTY_LICENSES.md`):** Stand auf `2026-09-30` re-auditiert mit formeller Querverlinkung zum Plain-Text-Begleiter `THIRD_PARTY_LICENSES.txt`.
- **NOTICE Querverweis:** Kanonische Querverlinkung auf `THIRD_PARTY_LICENSES.txt` ergänzt.
- **PEP 621 Standardisierung in `pyproject.toml`:** Erweiterung der `project.urls` um `Level 1 SBOM`, `Plain-Text License`, `Third-Party Licenses (Text)` und `Contributing`; Pytest-Konfiguration gehärtet (`addopts = "-ra -v --basetemp=.pytest_temp"`).
- **Gitignore Multi-Host- & Temp-Defense:** `.pytest_temp/` und `.pytest_tmp*/` in `.gitignore` hinterlegt.
- **Shields.io Badges & Metadaten-Synchronisation:** Badges für `Verified: 2026-09-30`, `Geprüft: 2026-09-30`, `Last-checked: 2026-09-30`, `Level 1 SBOM: Plain Text` und aktualisierte Testsuite-Zahlen synchronisiert.
- **Automatisierte Vertragstests:** Neue Contract-Tests in `tests/test_metadata.py` für ASCII-Topologieprojektion, Plain-Text Level 1 SBOM Invarianten INV-LOCAL-01..INV-SLA-10, PEP 621 Begleit-URLs und Pfad B Recency implementiert; Gesamt-Suite 100% grün.
- **Strikte Versions-Freeze-Disziplin:** Version `1.1.7` per T-20260920-167562623 strikt beibehalten.

### Headless CLI & Automation Interface (2026-09-29) - TW-UDG-03
- **Vollwertiges Headless-CLI-Interface (`cli.py`):** Neues zustands- und GUI-unabhängiges Kommandozeilenwerkzeug ermöglicht Skripting, Automatisierung und Hintergrundabfragen ohne X11/Windows-Display-Server.
- **CLI-Verben & Flags:**
  - `--version` / `-v`: Ausgabe der aktuellen Programmversion (`UniversalDocsGrabber 1.1.7`).
  - `--list-profiles`: Strukturierte Auflistung aller konfigurierten Suchprofile inkl. Gruppen, Account-Zuordnung, Betreff- und Gmail-Filtern.
  - `--list-accounts`: Sichere Auflistung aller hinterlegten IMAP-Konten mit strikt maskierten Passwörtern (`***MASKED***`).
  - `--list-documents`: Auflistung indexierter Dokumente mit Filterung nach Profil (`--profile`), Kategorie (`--category`) und Begrenzung (`--limit`).
  - `--export-library [PFAD]`: Headless-Export des redigierten PWA/Web-Companion-Katalogs gemäß Schema `docsgrabber-library-v1.json` ohne Plaintext-Secrets.
  - `--export-csv [PFAD]`: Export aller indexierten Dokumentmetadaten in eine tabellarische CSV-Datei mit UTF-8-BOM für Excel-Kompatibilität.
  - `--diagnose` / `--check-stack`: Vollständige Systemprüfung aller Verarbeitungs- und OCR-Komponenten (Poppler, Tesseract OCR, xhtml2pdf, pypdf, reportlab, Pillow, win32com, docx2pdf sowie Schreibrechte des Download-Zielordners).
  - `--json`: Formatierte maschinenlesbare JSON-Ausgabe auf stdout für AI-Agenten, Tool-Calling und Shell-Pipelines.
  - `--config` & `--documents-db`: Angabe benutzerdefinierter Konfigurations- und Datenbankdateien für Test- und Multimandantenbetrieb.
- **GUI-Interception vor Qt-Initialisierung:** `UniversalDocsGrabberV1.py` fängt CLI-Schalter in `main(argv)` vor der Erzeugung von `QApplication` und Qt-Fenstern ab.
- **Automatisierte Vertragstests:** 13 neue hermetische Unit- und Integrationstests in `tests/test_cli.py` (Gesamt-Testsuite: 148 Tests, 100% grün).

### Bugfixes & Konvertierungs-Resilienz (2026-09-28)
- **UniversalConverter Bildformate (.jpeg, .webp, .tif, .tiff):** `convert_to_pdf` unterstützt nun alle gängigen Bildformate inklusive `.jpeg`, `.webp`, `.tif` und `.tiff` (zuvor wurden `.jpeg`-Dateien mangels fehlendem Eintrag in der Formatliste abgewiesen).
- **Stale 0-Byte PDF-Bereinigung:** `convert_to_pdf` validiert bei bereits existierenden PDF-Dateien am Zielort (`output_path.stat().st_size > 0`) und räumt beschädigte oder leere 0-Byte-Dateileichen vorheriger abgebrochener Konvertierungen vor dem Neustart auf, statt leere Dateien fälschlicherweise als Erfolg zurückzugeben.
- **TXT-Mehrseiten-Paginierung & Format-Erhalt:** `convert_txt` überwacht nun über `t.getY()` die A4-Seitenhöhe (`t.getY() < 25*mm`), führt bei Textdokumenten mit mehr als einer Seite saubere Seitenumbrüche (`c.showPage()`) durch und verhindert das Abschneiden von Zeilen im negativen Koordinatenbereich; `line.rstrip('\r\n')` bewahrt Quelltext-Einrückungen und Tabulatoren.
- **Fehler-Bereinigung bei Konvertierungsabbrüchen:** `convert_txt`, `convert_img` und `convert_word` löschen unvollständige Ziel-PDFs bei Ausnahmen (`Path(o).unlink(missing_ok=True)`), um keine beschädigten Dateirückstände zu hinterlassen.
- **Anhang-Format-Normalisierung:** `is_format_allowed` normalisiert konfigurierte Download-Formate gegen führende Punkte (`.pdf` -> `pdf`), Großbuchstaben (`PDF` -> `pdf`) und unterstützt Bildformat-Aliase (`jpg`/`jpeg`, `tif`/`tiff`), sodass benutzerdefinierte Formatlisten zuverlässig greifen.
- **Datenmodell-Resilienz & Schemakompatibilität:** `SearchProfile.from_dict`, `MailAccount.from_dict`, `DownloadSettings.from_dict` und `Document.from_dict` filtern unbekannte Schlüssel defensiv gegen Dataclass-Felder und mutieren übergebene Eingabe-Dictionaries nicht mehr in-place (`d_copy = dict(d)`).
- **Dateinamen-Sanitisierung auf Windows:** `sanitize_filename` bereinigt nachgestellte Punkte und Leerzeichen (`.rstrip('. ')`) und sichert reservierte Windows-/DOS-Gerätenamen (`CON`, `PRN`, `AUX`, `NUL`, `COM1-9`, `LPT1-9`) mit sicherem Präfix `file_` ab.
- **Automatisierte Regressionstests:** 7 neue hermetische Regressionstests in `tests/test_bugsweep_converter_and_format_resilience_20260928.py` (Vollsuite: 135/135 Tests 100% grün).

### Software Security & License Audit (2026-09-28)
- **Dependency Floors & Schwachstellen-Schutz:** `pypdf>=4.0.0` (Schutz vor veralteten 3.x Parser-DoS-Advisories), `Pillow>=10.4.0` (Schutz vor bekannten Libwebp/Image-Parser CVEs), `keyring>=25.0.0`, `PySide6>=6.5.0` in `requirements.txt` und `pyproject.toml` gehärtet.
- **PEP 621 Standard-Abhängigkeiten & Build-Floors:** `pyproject.toml` um `dependencies` sowie `[project.optional-dependencies]` für `dev` (`pytest>=9.1.1`, `ruff>=0.9.0`) und `build` (`pyinstaller>=6.10.0`, `altgraph>=0.17.4`, `packaging>=24.0`) erweitert; Autoren-Email um `support@lukasgeiger.com` ergänzt; `requirements-dev.txt` angelegt.
- **Standardisiertes Drittanbieter-Lizenzinventar:** `THIRD_PARTY_LICENSES.txt` nach dem standardisierten 5-Felder-Schema (`Package:`, `License:`, `SPDX:`, `URL:`, `Notice:`) für alle 24 Komponenten (PySide6, Qt6, shiboken6, pypdf, reportlab, Pillow, xhtml2pdf, keyring, pytesseract, pdf2image, pywin32, docx2pdf, Tesseract OCR, Poppler, pytest, pluggy, iniconfig, ruff, PyInstaller, altgraph, packaging, setuptools) ausgebaut; MIT-Lizenzkompatibilität und Subprozess-Isolation formal verifiziert.
- **Sicherheitsrichtlinie (SECURITY.md) gehärtet:** Zweisprachige Security-Policy (English & Deutsch) mit privatem Advisory-Link (`https://github.com/doc-bricks/UniversalDocsGrabber/security/advisories/new`), offiziellen Kontakten (`security@doc-bricks.org`, `security@open-bricks.org`, `security@ellmos.ai`, `support@lukasgeiger.com`), verbindlichem 48h-SLA für Erstbestätigung, 5 Werktagen Triage-SLA und formellen Local-First/Zero-Egress- sowie Non-Elevation (`RunAsInvoker`) Invarianten etabliert.
- **Gitignore-Sicherheitshärtung:** `.gitignore` um Zertifikats-Muster (`*.pfx`, `*.p12`, `*.cer`, `*.crt`), Secrets (`secrets.*`, `keyring/`), Sync-Konfliktmuster (`*-conflict-*`, `*-CONFLIT-*`) und Test-Artefakt-Muster (`pytest_out.txt`, `pytest*.txt`) erweitert.
- **Pfad- und Secret-Hygiene:** Vollständiger Code-Scan belegt 0 absolute persönliche Windows-Nutzerpfade und 0 Klartext-Secrets im gesamten Repository.
- **Automatisierte Vertragstests:** Neue Testsuite `tests/test_security_license_contract.py` mit 8 Contract-Tests implementiert; Gesamt-Suite auf 128 automatisierte Tests erweitert (128/128 passed, 100% grün).

### Pfad B Marketing, Discoverability, Visual Architecture & Bilateral Navigation Parity (2026-09-28)
- **18-Punkte-Bilateralnavigation mit dualen HTML-Ankern:** Vollständige strukturelle Parität zwischen `README.md` und `README-DE.md` mit wechselseitigen Hyperlinks (#1..#18) und dualen Ankern (`<a id="sec-01"></a>` bis `<a id="sec-18"></a>`) sowie Erhalt aller bestehenden Anker-Aliase.
- **Level 1 SBOM Invarianten-Kreuzreferenzmatrix:** `THIRD_PARTY_LICENSES.md` um Abschnitt 8 erweitert, der alle zehn Governance- und Laufzeit-Invarianten (`INV-LOCAL-01` bis `INV-SLA-10`) tabellarisch abbildet, die unprivilegierte `RunAsInvoker`-Ausführung zertifiziert und die Zero-Copyleft-Isolation garantiert.
- **PEP 621 Metadaten & 20-Topic-Sättigung:** `pyproject.toml` um alle 20 GitHub-Repository-Topics in `keywords` erweitert und kanonische `Homepage`-URL mit `#readme`-Anker verankert.
- **Gesetzlicher Haftungsausschluss (§ 521 BGB Gefälligkeitsrecht) & 48h Security Response SLA:** Formale Haftungsbegrenzung nach deutschem Zivilrecht (§ 521 BGB) und verbindliche 48h-Erstquittierungs-SLA in Abschnitt 18 beider READMEs sowie in `SECURITY.md` verankert.
- **llms.txt Kontext-Index Aktualisierung:** Letztes Prüfdatum auf `2026-09-28` aktualisiert, Teststand-Baseline auf 116 Tests angehoben und Level 1 SBOM Notizen integriert.
- **Automatisierte Vertragstests:** `tests/test_metadata.py` um Prüfungen für die 18-Punkte-Navigation mit dualen Ankern, Level 1 SBOM Invariantenmatrix, PEP-621-Keywordsättigung und § 521 BGB Disclaimer erweitert.
- **Strikte Versions-Freeze-Disziplin:** Version `1.1.7` per T-20260920-167562623 strikt unverändert beibehalten.

### App-Icons, Multi-Layer ICOs & Mobile PWA Suite (2026-09-26)
- **Multi-Resolution Windows Explorer ICOs:** Vollwertige 7-Layer `.ico`-Dateien (`UniversalDocsGrabber_icon.ico`, `UniversalDocsGrabber.ico`, `DesktopIcon.ico`, `icon.ico`, `ICO.ico`, `assets/UniversalDocsGrabber_icon.ico`, `assets/UniversalDocsGrabber.ico`, `assets/DesktopIcon.ico`, `assets/icon.ico`, `assets/app_icon.ico`) mit 16x16, 24x24, 32x32, 48x48, 64x64, 128x128 und 256x256 Pixeln bei 32bpp RGBA erzeugt bzw. aktualisiert (schließt die bisher fehlende 24x24-Ebene für Windows 10/11 Taskleiste und Explorer).
- **Master-PNGs & Favicon-Parität:** Hochauflösende 1024x1024 RGBA Master-Icons (`UniversalDocsGrabber.png`, `UniversalDocsGrabber_icon.png`, `DesktopIcon.png`, `icon.png`, `assets/UniversalDocsGrabber.png`, `assets/UniversalDocsGrabber_icon.png`, `assets/DesktopIcon.png`, `assets/icon.png`) verankert sowie 4-Layer `favicon.ico` (16, 24, 32, 48 px) und Web-Favicons `favicon.png` (32x32 px) in Root, `assets/` und `mobile_icons/` bereitgestellt.
- **PWA & Mobile Icon Suite (`mobile_icons/`):** Vollständiges mobiles Icon-Paket inklusive W3C `manifest.json`, Standard-Icons (`icon-192.png`, `icon-512.png`), maskierbaren Varianten (`icon-maskable-192.png`, `icon-maskable-512.png`) mit 80%-Safe-Zone auf Theme-Hintergrund, Apple-Touch-Icons (180x180 px), Favicons und Unterordner `icons/` angelegt.
- **Laufzeit-Icon-Integration:** `app_icon_loader.py` mit `load_app_icon()` und `get_app_icon()` für robustes Multi-Pfad-Fallback (PyInstaller `_MEIPASS`, `assets/app_icon.ico`, `assets/UniversalDocsGrabber_icon.ico`, Root-ICOs und PNG-Fallback) implementiert; in `UniversalDocsGrabberV1.py` in `MainWindow.setup_ui()` via `setWindowIcon()` und im App-Startblock via `app.setWindowIcon()` verdrahtet.
- **Packaging & Build-Spec:** `UniversalDocsGrabber.spec` mit Icon-Bindung (`UniversalDocsGrabber_icon.ico`) und Asset-Bündelung erstellt.
- **Automatisierte Vertragstests:** 5 neue Contract-Tests in `tests/test_assets_and_icons.py` (Master-Icons, Multi-Layer ICO Binary-Header-Parsing, Assets-Parität, Mobile/PWA-Manifest und Laufzeit-Iconloader). Vollsuite auf 116 Tests erweitert (116/116 passed, 100% grün).

### Bugfixes & Grabber-Resilienz (2026-09-25)
- **Query Builder Phrasen-Trennung:** `QueryBuilderDialog._parse_comma_separated_input` trennt Benutzereingaben nun strikt an Kommas statt an allen Leerzeichen (`text.split(",")`), sodass mehrteilige Suchphrasen (z. B. `"Telekom Deutschland, Allianz Global"`) erhalten und korrekt in Gmail-Syntax (`"..."`) quotiert werden.
- **Header-Extraktion & Absender-Resilienz:** `_parse_email_metadata` extrahiert bei Absender-Headern ohne Display-Namen (`<service@paypal.de>`) nun zuverlässig die E-Mail-Adresse zwischen den Klammern statt einen leeren String zurückzugeben.
- **Datums-Parsing auf Windows:** Pre-1970 Zeitstempel und historische/ungültige Datumsangaben werden in `_parse_email_metadata` über Kalenderkomponenten formatiert und gegen `OSError: [Errno 22] Invalid argument` abgesichert.
- **Auto-Kategorisierung Umlaute:** `_auto_categorize` um die deutschen Standard-Keywords `"kündigung"` und `"verträge"` erweitert.
- **Kategorie-Ableitung:** Fallthrough-Fehler in `infer_document_category` behoben, durch den fremde Unterordner fälschlich als Kategorie des Profils zurückgegeben wurden.
- **Mail-Body-Extraktion & Fehler-Bereinigung:** `_convert_body_to_pdf` ignoriert nun HTML- und Text-Anhänge beim Ermitteln des Mail-Bodys und fängt unvorhergesehene Exceptions in `pisa.CreatePDF` sauber ab, wobei 0-Byte-Dateien restlos vom Datenträger gelöscht werden.
- **IMAP-Filter & Control-Character-Härtung:** `build_imap_search_args` und `build_gmail_raw_query` prüfen auf nicht-leere getrimmte Werte (`query_sender`, `query_subject`) und verhindern leere Wildcard-Kriterien (`FROM ""` / `SUBJECT ""`); `_quote_imap_string` filtert Zeilenumbrüche (`\r`, `\n`).
- **Deduplizierung & DB-Synchronisation:** `run_deduplication` prüft mit `is_file()` und verhindert `PermissionError` auf Ordnern mit Punkten; gelöschte Duplikate werden synchron aus `self.db` entfernt.
- **Regressionstests:** 9 neue automatisierte Regressionstests in `tests/test_bugsweep_grabber_resilience_20260925.py`.

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
