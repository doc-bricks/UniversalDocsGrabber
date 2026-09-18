# Windows Store Release Readiness & Bewertung (TW-UDG-01 / TASKPLAN #1151)

Stand: 2026-09-18  
Status: **READY FOR MSIX PACKAGING (VOLLSTÄNDIG GESTAGT)**

## 1. Executive Summary & Einstufung

UniversalDocsGrabber ist als lokale PyQt6-Desktop-Anwendung für Windows konzipiert.
Die Store-Bereitstellung erfolgt über das Windows App SDK / MSIX Desktop-Bridge-Verfahren mit `runFullTrust` und `internetClient`-Capabilities.

### Bewertungsurteil: **READY FOR MSIX PACKAGING**
- Die Kernapplikation erfüllt alle lokalen Sicherheits- und Datenschutzanforderungen.
- Keine Telemetrie, keine unerlaubten Hintergrundnetzwerkdienste, keine Registry-Verschmutzung außerhalb von AppData.
- Credentials werden über den Windows Credential Vault (`keyring`) sicher und isoliert abgelegt.
- Richtlinie 10.1.3 des Microsoft Partner Centers für Store-Listings (Suchbegriffe / Keywords) ist formal auf 7 markenrechtsfreie Begriffe je Sprache festgesetzt und validiert.
- Multi-Resolution Store Tile-Assets (44x44, 50x50, 150x150, 310x150, 310x310), 1080p Screenshots und Desktop-Bridge `AppxManifest.xml` liegen vollständig vor.
- Release-Staging-Ordner `releases/windowsstore/` mit `BUILD.md`, `WACK_PROTOCOL.md`, `store_settings.json`, `store_listing_de.md`, `store_listing_en.md` und `StoreLogo.png` ist aufgebaut.

## 2. Capabilities & Berechtigungen

| Capability | Begründung & Verwendung |
|---|---|
| `runFullTrust` | Erforderlich für Desktop-Dateisystemzugriff (Speichern in Zielordnern), Subprozess-Ausführung von Tesseract/Poppler (OCR) und Word-COM-Schnittstelle. |
| `internetClient` | Erforderlich für ausgehende IMAP-SSL-Verbindungen (Port 993) zum E-Mail-Server des Nutzers. |

Keine weiteren Capabilities (wie Webcams, Mikrofone, Standort) werden angefordert oder benötigt.

## 3. Optionale Komponenten & Systemvoraussetzungen

1. **OCR-Stack (Tesseract / Poppler):**
   - UniversalDocsGrabber stürzt bei fehlendem Tesseract/Poppler nicht ab. Es greift ein klarer Fehler-Fallback mit informativem Logeintrag (`LOG_MSG_OCR_UNAVAILABLE`).
   - Ein Bundle im MSIX ist optional, jedoch nicht verpflichtend, da die Basis-Dokumentensammlung auch ohne OCR voll funktionsfähig ist.
2. **Office-Konvertierung:**
   - Falls kein Microsoft Word / `win32com` installiert ist, wird auf `docx2pdf` oder die Speicherung im Originalformat zurückgefallen.
3. **Plattform-Neutralität & Companion:**
   - Der Web/PWA-Companion (`web_companion/`) operiert auf dem redigierten JSON-Format `docsgrabber-library-v1.json`, welches vollkommen frei von Zugangsdaten ist.

## 4. Store-Paketierungs- und Metadaten-Matrix

- **Publisher Identity:** `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`
- **Publisher Display Name:** `Geiger`
- **Identity Name:** `Geiger.UniversalDocsGrabber`
- **Version:** `1.1.7.0`
- **Executable:** `UniversalDocsGrabber.exe` (erzeugt via `build_exe.bat`)
- **Manifest:** `store_package/UniversalDocsGrabber/AppxManifest.xml`
- **Tile-Assets:** `store_assets/` und `store_package/UniversalDocsGrabber/assets/` (44x44, 50x50, 150x150, 310x150, 310x310)
- **Screenshots:** `screenshots/store/` und `releases/windowsstore/screenshots/` (4x 1920x1080)
- **Listing-Dateien:** `STORE_LISTING.md`, `PRIVACY.md`, `SUPPORT.md`, `store_package.json`, `releases/windowsstore/`
- **Asset-Generator:** `scripts/generate_store_assets.py`
- **Preflight-Checker:** `scripts/check_store_readiness.py` (31/31 Checks bestanden)
- **Vertragstests:** `tests/test_store_materials.py` (11 Tests) & `tests/test_store_readiness.py` (1 Test)

## 5. Nächste Schritte vor finaler Einreichung

1. Ausführung von `build_exe.bat` zur Erzeugung der Release-EXE `dist\UniversalDocsGrabber.exe`.
2. Packen mit `_STORE/msstore_build_msix.ps1` zur Erstellung des signierten MSIX-Pakets `UniversalDocsGrabber.msix`.
3. WACK-Ausführung (Windows App Certification Kit) gemäß `releases/windowsstore/WACK_PROTOCOL.md`.
4. Upload des MSIX-Pakets in das Microsoft Partner Center unter der reservierten App-ID.
