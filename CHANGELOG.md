# Changelog / Änderungsprotokoll

Alle wesentlichen Änderungen an diesem Projekt werden hier dokumentiert.
Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.1.0/).

## [Unreleased]

### Hinzugefügt / Added
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
