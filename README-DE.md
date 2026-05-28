# UniversalDocsGrabber

**Automatischer Download und Verwaltung von Dokumenten aus IMAP-E-Mails**

> **English documentation:** [README.md](README.md)

![Status](https://img.shields.io/badge/status-freigegeben-green)
![Python](https://img.shields.io/badge/python-3.8+-blue)
![Platform](https://img.shields.io/badge/platform-Windows%20Desktop-lightgrey)

![UniversalDocsGrabber Screenshot](README/screenshots/main.png)

## Überblick

UniversalDocsGrabber ist eine PySide6-Desktop-Anwendung für den Download, die Konvertierung und die Ablage von Dokumenten aus IMAP-Postfächern.

## Kernfunktionen

- Multi-Account IMAP Support
- Suchprofile mit Filtern für Absender, Betreff und Zeitraum
- Download von PDF, DOCX, DOC, JPG, PNG und weiteren Dokumenttypen
- Automatische Konvertierung nach PDF
- OCR für PDFs ohne Textebene
- Hash-basierte Duplikate-Erkennung
- Scheduler für wiederkehrende Scans von 15 Minuten bis 24 Stunden
- Auto-Kategorisierung mit Standard- und benutzerdefinierten Regeln
- Drag&Drop-Sortierung von Profilen und Batch-Läufe für alle aktiven Profile
- Gmail-Raw-Queries werden auf Servern mit `X-GM-RAW` mit Absender-,
  Betreff- und Datumsfiltern kombiniert; andere IMAP-Server fallen sauber auf
  klassische `FROM`/`SUBJECT`/`SINCE`-Suchen zurück
- Lokale Speicherung von Kontoeinstellungen und Dokumentmetadaten
- Redigierter Export `docsgrabber-library-v1.json` für den lokalen Web/PWA-Companion
- Klarer beschriftete Tabs, Löschaktionen und Tooltips verringern
  Fehlbedienungen bei Profilen, Konten und Download-Pfaden

## Datenschutzmodell

UniversalDocsGrabber läuft lokal auf dem Windows-Rechner. Mail-Zugangsdaten werden, sofern verfügbar, im Betriebssystem-Keyring gespeichert; Projekt- und Dokumentmetadaten liegen im Benutzerprofil. Die Anwendung enthält keine Telemetrie, keinen Cloud-Dienst und kein gehostetes Backend.

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

### Optional: Poppler

1. Download: <https://github.com/oschwartz10612/poppler-windows/releases>
2. Nach `C:\Program Files\poppler\` entpacken
3. Falls nötig `POPPLER_PATH` in `UniversalDocsGrabberV1.py` anpassen

### Optional: Tesseract

1. Download: <https://github.com/UB-Mannheim/tesseract/wiki>
2. Nach `C:\Program Files\Tesseract-OCR\` installieren
3. Zum `PATH` hinzufügen

## Nutzung

```bash
python UniversalDocsGrabberV1.py
```

oder `START.bat` per Doppelklick.

## Typischer Workflow

1. IMAP-Konto im Tab `Konten` anlegen
2. Suchprofil mit Gruppe, Filtern und Zielordner erstellen
3. Zeitfilter setzen
4. Einzelprofil starten oder alle aktiven Profile mit `START` scannen
5. Dokumente im Tab `Dokumente` durchsuchen
6. Über `Einstellungen -> Companion-Export -> Redigierten Export speichern...`
   einen redigierten Bibliotheks-Snapshot erzeugen
7. Optional `web_companion/index.html` lokal öffnen oder per `?demo=1` den
   Companion ohne echten Export prüfen

## Funktionen im Detail

### Suchprofile

- Gruppen für thematische Sortierung
- Drag&Drop-Sortierung zwischen Gruppen
- Profil-spezifische Override-Einstellungen
- Zeitfilter pro Lauf

### Konvertierung

- Word zu PDF via `win32com` oder `docx2pdf`
- TXT zu PDF via `reportlab`
- Bilder zu PDF via Pillow
- OCR für PDFs ohne Textebene

### Scheduler & Auto-Kategorisierung

- Wiederkehrende Scans von 15 Minuten bis 24 Stunden
- Läufe werden übersprungen, wenn bereits ein Scan aktiv ist
- Batch-Ausführung verarbeitet alle aktiven Profile accountweise gruppiert
- Regelbasierte Auto-Kategorisierung für Rechnungen, Versand, Verträge, Kündigungen, Steuer, Versicherung, Bewerbungen und Bank

### Deduplizierung

- SHA-256 Hash-Check
- Optional pro Profil aktivierbar

## Lokale Daten

- `%USERPROFILE%\.univ_docs_grabber\config_v1.json`
- `%USERPROFILE%\.univ_docs_grabber\documents.json`
- `%USERPROFILE%\Downloads\UnivDocs\`

Diese Dateien bleiben absichtlich außerhalb von Git, weil sie Kontoangaben, lokale Pfade, Dokumentmetadaten und heruntergeladene Dokumente enthalten können.

## Bekannte Grenzen

- OCR benötigt Tesseract und Poppler
- Word-Konvertierung benötigt Windows-Komponenten
- Die Suche arbeitet bewusst konservativ mit begrenzter Mail-Menge pro Profil

## Plattformstrategie

Die Windows-Desktop-App bleibt die Vollversion für IMAP-Zugriff, OCR,
Konvertierung, Scheduler und lokale Dateiablage. macOS und Linux werden als
Source-Smoke-Ziele geplant. Web, Android und iOS sollen später über einen
Web/PWA-Companion mit redigiertem `docsgrabber-library-v1.json`-Export laufen.
Der statische Companion unter `web_companion/` bietet bereits lokalen Import,
Suche, Profil-/Kategorienansichten und mobile Dokumentkontrolle, nicht jedoch
einen nativen Mail-Abruf.

Der Export enthält Profile, Kategorien, Dokumentmetadaten, Profilstatistiken und
redigierte Pfadhinweise, aber keine Credentials, Dokumentinhalte oder
Mail-Body-Volltexte.

Siehe [PORTIERUNGSPLAN.md](PORTIERUNGSPLAN.md) und [EXPORTFORMAT.md](EXPORTFORMAT.md).

## Projektstruktur

```text
REL-PUB_UniversalDocsGrabber/
|-- UniversalDocsGrabberV1.py
|-- START.bat
|-- requirements.txt
|-- README.md
|-- README-DE.md
`-- README/screenshots/main.png
```

## Entwicklung

```bash
python -m pytest -q
python -m py_compile UniversalDocsGrabberV1.py
```

## Verwandte Tools

Teil der [doc-bricks](https://github.com/doc-bricks) Mail-Suite:

| Tool | Beschreibung |
|------|--------------|
| [MailProcessor](https://github.com/doc-bricks/MailProcessor) | System-Tray-Launcher für alle Universal Mail Tools |
| [UniversalMailCleaner](https://github.com/doc-bricks/UniversalMailCleaner) | Regelbasierter IMAP-Cleaner mit Safe-Mode |
| [UniversalInvoiceMail](https://github.com/doc-bricks/UniversalInvoiceMail) | Rechnungen und Belege automatisch aus Mails extrahieren |

## Lizenz

[MIT](LICENSE) - Lukas Geiger
