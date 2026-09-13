# Windows Store Release Readiness & Bewertung (TW-UDG-01 / TASKPLAN #1151)

Stand: 2026-09-10  
Status: Bewertet & Vorbereitet (Readiness-Artefakte formalisiert)

## 1. Executive Summary & Einstufung

UniversalDocsGrabber ist als lokale PyQt6-Desktop-Anwendung für Windows konzipiert.
Die Store-Bereitstellung erfolgt über das Windows App SDK / MSIX Desktop-Bridge-Verfahren mit `runFullTrust` und `internetClient`-Capabilities.

### Bewertungsurteil: **READY FOR PACKAGING (VORBEREITET)**
- Die Kernapplikation erfüllt alle lokalen Sicherheits- und Datenschutzanforderungen.
- Keine Telemetrie, keine unerlaubten Hintergrundnetzwerkdienste, keine Registry-Verschmutzung außerhalb von AppData.
- Credentials werden über den Windows Credential Vault (`keyring`) sicher und isoliert abgelegt.
- Richtlinie 10.1.3 des Microsoft Partner Centers für Store-Listings (Suchbegriffe / Keywords) ist formal auf 7 markenrechtsfreie Begriffe je Sprache festgesetzt und validiert.

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
- **Listing-Dateien:** `STORE_LISTING.md`, `PRIVACY.md`, `SUPPORT.md`, `store_package.json`
- **Preflight-Checker:** `scripts/check_store_readiness.py`
- **Vertragstests:** `tests/test_store_readiness.py`

## 5. Nächste Schritte vor finaler Einreichung

1. Ausführung von `build_exe.bat` zur Erzeugung der Release-EXE `dist\UniversalDocsGrabber.exe`.
2. Packen mit `WinStorePackager` zur Erstellung des signierten MSIX-Pakets.
3. WACK-Ausführung (Windows App Certification Kit) auf einem isolierten Windows-System.
4. Upload des MSIX-Pakets in das Microsoft Partner Center unter der reservierten App-ID.
