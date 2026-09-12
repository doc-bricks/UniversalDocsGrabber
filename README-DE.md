<img src="assets/banner.png" width="100%" alt="UniversalDocsGrabber — Automatischer Dokumenten-Download aus jeder Quelle">

# UniversalDocsGrabber

**Automatischer Download und Verwaltung von Dokumenten aus IMAP-E-Mails**

UniversalDocsGrabber ist ein lokaler E-Mail-Anhang-Downloader und
Dokumenten-Organizer für Windows. Das Tool verbindet sich mit IMAP- oder
Gmail-kompatiblen Postfächern, lädt PDF-, Office-, Bild- und Mail-Body-Dokumente
herunter, konvertiert sie bei Bedarf nach PDF, erkennt Duplikate per
SHA-256-Hash und hält den Dokumentindex auf dem eigenen Rechner.

> **English documentation:** [README.md](README.md)

[![Version: 1.1.6](https://img.shields.io/badge/Version-1.1.6-blue.svg)](pyproject.toml)
[![CI](https://github.com/doc-bricks/UniversalDocsGrabber/actions/workflows/ci.yml/badge.svg)](https://github.com/doc-bricks/UniversalDocsGrabber/actions/workflows/ci.yml)
[![Contract-Tests](https://img.shields.io/badge/contract--tests-108%20bestanden-brightgreen.svg)](tests/)
[![Lizenz: MIT](https://img.shields.io/badge/Lizenz-MIT-yellow.svg)](LICENSE)
[![Plattform](https://img.shields.io/badge/plattform-Windows%20%7C%20macOS%20%7C%20Linux-blue)](https://github.com/doc-bricks/UniversalDocsGrabber)
[![Python](https://img.shields.io/badge/python-3.8%20%7C%203.9%20%7C%203.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://www.python.org/)
[![LLM-Ready](https://img.shields.io/badge/LLM--Ready-llms.txt-purple.svg)](llms.txt)
[![Datenschutz](https://img.shields.io/badge/Datenschutz-100%25%20Offline%20%7C%20Zero--Egress-success.svg)](README-DE.md#datenschutzmodell)
[![Sicherheit](https://img.shields.io/badge/Sicherheit-Lokal--First%20%7C%20Keyring-blue.svg)](SECURITY.md)
[![Sicherheits-SLA](https://img.shields.io/badge/Sicherheits--SLA-48h%20%7C%205d%20Triage-brightgreen.svg)](SECURITY.md)
[![Drittanbieter-Lizenzen](https://img.shields.io/badge/Drittanbieter--Lizenzen-100%25%20Zul%C3%A4ssig-blue.svg)](THIRD_PARTY_LICENSES.md)
[![Marketing-Log](https://img.shields.io/badge/Marketing--Log-Aktiv%20%7C%20Gepr%C3%BCft-blue.svg)](MARKETING-LOG.txt)
[![doc-bricks](https://img.shields.io/badge/organisation-doc--bricks-blue.svg)](https://github.com/doc-bricks)
[![open-bricks](https://img.shields.io/badge/%F0%9F%A7%B1_ecosystem-open--bricks-blue)](https://github.com/open-bricks)
[![Letzte Prüfung](https://img.shields.io/badge/Letzte--Pr%C3%BCfung-2026--09--12-informational.svg)](llms.txt)

| [⚡ Schnellstart](#einstieg) | [🏗️ Architektur & Datenfluss](#systemarchitektur--datenfluss) | [🔄 Lebenszyklus-Ablauf](#end-to-end-dokumenten-lebenszyklus) | [📋 Governance- & Laufzeit-Invarianten](#governance--und-laufzeit-invarianten) | [✨ Funktionen im Detail](#funktionen-im-detail) | [⚙️ Installation & Einrichtung](#installation--einrichtung) | [🔄 Typischer Arbeitsablauf](#typischer-arbeitsablauf) | [🔒 Datenschutz & Sicherheit](#datenschutzmodell) | [📱 Web/PWA-Begleiter](#plattform-strategie) | [🧩 Geschwister-Werkzeuge](#ökosystem--geschwister-tools) | [📜 Drittanbieter-Lizenzen](#drittanbieter-lizenzen--transparenz) | [🎯 Zielgruppen](#marketing--zielgruppen) | [⚠️ Bekannte Einschränkungen](#bekannte-einschränkungen) | [🛡️ Sicherheitsrichtlinie](SECURITY.md) | [🤖 LLM-Kontext](llms.txt) |

Aktueller Contract-Readback (2026-09-12): 76 Pytest-Tests und 32 Node-Tests des
Web-Companions sind grün (108 Contract-Tests gesamt, 100% bestanden). Installation,
Offline-Start und Lesbarkeit auf Android/iOS bleiben getrennte Geräte-/Emulator-
Gates. Die plattformübergreifende Statusmatrix steht in
[`PORTIERUNGSPLAN.md`](PORTIERUNGSPLAN.md).

Das Badge `108 bestanden` zählt die 76 Python- und 32 Node-Contract-Tests;
vollständige CI-Matrix-Tests auf Windows, Ubuntu und macOS laufen bei jedem Commit.

> [!NOTE]
> **KI / LLM Integration & Lokales Datenschutzmodell**: UniversalDocsGrabber arbeitet 100 % lokal. Zugangsdaten liegen sicher im Windows Credential Vault. Der statische Web/PWA-Companion nutzt ein redigiertes Exportformat (`docsgrabber-library-v1.json`), das Zugangsdaten, E-Mail-Texte und PDF-Inhalte strikt ausschließt — ideal für mobilen Review oder KI-gestützte Dokumenten-Audits. Das vollständige KI-Schema ist in [`llms.txt`](llms.txt) und [`EXPORTFORMAT.md`](EXPORTFORMAT.md) beschrieben.

![UniversalDocsGrabber Screenshot](README/screenshots/main.png)


![UniversalDocsGrabber Web/PWA Companion Screenshot](README/screenshots/web-companion-demo.png)

## Einstieg

| Bedarf | Einstieg |
|--------|----------|
| Wiederkehrende Rechnungs-, Versicherungs-, Steuer-, Vertrags- oder Versanddokumente aus Postfächern sammeln | `python UniversalDocsGrabberV1.py` |
| Eine redigierte Dokumentbibliothek auf einem anderen Gerät prüfen, ohne Mail-Zugangsdaten offenzulegen | `web_companion/index.html?demo=1` |
| Das Companion-Exportformat integrieren oder prüfen | [EXPORTFORMAT.md](EXPORTFORMAT.md) |
| Am Projekt mitwirken | [CONTRIBUTING.md](CONTRIBUTING.md) |

## Überblick

UniversalDocsGrabber ist eine PySide6-Desktop-Anwendung für den Download, die Konvertierung und die Ablage von Dokumenten aus IMAP-Postfächern.

Typische Einsätze sind Rechnungsablage, Vertragsarchiv, Versicherungs- und
Steuerpost, Bewerbungsunterlagen, Versandnachweise und andere wiederkehrende
Mailbox-zu-Ordner-Workflows.

## Warum UniversalDocsGrabber

- **Für Mailbox-Dokumente gebaut:** IMAP-Profile, Gmail-Raw-Queries,
  Absender-/Betreff-/Datumsfilter, Anhang-Download, PDF-Konvertierung, OCR und
  Kategorisierung liegen in einem Desktop-Workflow.
- **Privat voreingestellt:** Kontoeinstellungen und Dokumentmetadaten bleiben
  lokal; Exporte für den Web/PWA-Companion sind redigiert und enthalten keine
  Credentials, Mail-Body-Volltexte oder Dokumentdateien.
- **Auch mobil prüfbar:** Der statische Web/PWA-Companion öffnet einen
  redigierten `docsgrabber-library-v1.json`-Export für Suche, Statuskontrolle
  und Review, ohne den Browser zum Mail-Client zu machen.

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

## Systemarchitektur & Datenfluss

```mermaid
graph TD
    A["IMAP / Gmail Postfach"] -->|SSL / TLS Verbindung| B["IMAP Such-Engine"]
    B -->|Absender, Betreff, Datumsfilter| C["Extraktor für Anhänge & Mailtexte"]
    C -->|SHA-256 Hashprüfung| D{"Duplikat vorhanden?"}
    D -->|Ja| E["Download überspringen"]
    D -->|Nein| F["Dokumenten-Pipeline"]
    F -->|Word / TXT / Bilder| G["PDF Konverter-Engine"]
    F -->|Gescannte PDFs| H["Tesseract OCR-Engine"]
    G --> I["Lokales Archiv & SQLite-Index"]
    H --> I
    I --> J["Generator für redigierte Exporte"]
    J --> K["Statischer Web / PWA-Begleiter"]
```

### End-to-End Dokumenten-Lebenszyklus

```mermaid
sequenceDiagram
    autonumber
    actor User as "Nutzer / Scheduler"
    participant App as "UniversalDocsGrabber Desktop"
    participant Vault as "Windows Credential Vault"
    participant IMAP as "IMAP / Gmail Postfach"
    participant Pipeline as "Konvertierungs- & OCR-Pipeline"
    participant Storage as "Lokales Archiv & SQLite DB"
    participant PWA as "Web / PWA-Begleiter"

    User->>App: "Scan starten (Manuell / Zeitplan)"
    App->>Vault: "Zugangsdaten anfragen"
    Vault-->>App: "Entschlüsseltes Keyring-Geheimnis"
    App->>IMAP: "SSL/TLS verbinden & Filter abfragen (FROM/SUBJECT/SINCE)"
    IMAP-->>App: "Passende Nachrichten & Anhänge"
    loop Für jeden Anhang
        App->>App: "SHA-256 Hash berechnen"
        alt Hash im lokalen Index vorhanden
            App->>App: "Duplikat überspringen"
        else Neues Dokument
            App->>Pipeline: "Nach MIME / Dateityp routen"
            Pipeline->>Pipeline: "Word/TXT/Bild zu PDF oder Tesseract OCR"
            Pipeline-->>Storage: "Normalisiertes PDF speichern & DB aktualisieren"
        end
    end
    opt Redigierter mobiler Review
        User->>App: "Redigierten Export erzeugen"
        App->>Storage: "docsgrabber-library-v1.json schreiben (Null Credentials)"
        Storage-->>PWA: "Lokal öffnen (100% Client-seitige Prüfung)"
    end
```

## Governance- und Laufzeit-Invarianten

Die Software unterliegt zehn verbindlichen Architektur- und Betriebsregeln:

| ID | Invariante | Beschreibung & Architekturgrenze | Durchsetzung & Nachweis |
|---|---|---|---|
| `INV-LOCAL-01` | **Local-First & Zero-Egress** | 100% Offline-Dokumentenverarbeitung, OCR und PDF-Generierung. Keine Netzwerk-Telemetrie. | Keine externen HTTP-Verbindungen beim Ingestion-Lauf; air-gap-fähig |
| `INV-SEC-02` | **RunAsInvoker-Privilegiengrenze** | Läuft strikt im unprivilegierten Benutzerkontext. Fordert niemals Administrator-Rechte an. | Unprivilegiertes Ausführungsprofil |
| `INV-CRED-03` | **Betriebssystem-Keyring** | Passwörter und OAuth-Tokens werden verschlüsselt im Windows Credential Vault abgelegt; kein Klartext. | `keyring`-Integration |
| `INV-REDACT-04` | **Sanitisiertes Export-Schema** | Mobiler Export `docsgrabber-library-v1.json` schließt Zugangsdaten, Tokens und Mail-Texte strikt aus. | `test_export_format.py` & JSON-Schemavalidierung |
| `INV-HASH-05` | **SHA-256 Duplikatsprüfung** | Kryptografischer Inhalts-Hash verhindert mehrfaches Herunterladen und Speichern identischer Dokumente. | `hashlib.sha256`-Prüfung |
| `INV-FALL-06` | **Robuste Fallbacks** | Saubere Protokollierung und Weiterführung, wenn optionale Module (Word, Poppler, Tesseract) fehlen. | `tests/source_platform_smoke.py` |
| `INV-PWA-07` | **Abhängigkeitsfreie PWA** | Statischer Begleiter nutzt native Browser-APIs, Service Worker und 0 externe CDN/NPM-Pakete. | `web_companion/package.json` (0 Dependencies) |
| `INV-LIC-08` | **100% Zulässige Open-Source** | MIT-Basis mit transparenter dynamischer LGPLv3-Verlinkung und Ersetzungsfreiheit für Qt-Bibliotheken. | `THIRD_PARTY_LICENSES.md` |
| `INV-SLA-09` | **48h Sicherheits-SLA** | Eingangsbestätigung von Sicherheitsmeldungen binnen 48h; Triage binnen 5 Werktagen. | `SECURITY.md` Richtlinie |
| `INV-PAR-10` | **Zweisprachige Vertragsparität** | Vollständige Symmetrie zwischen deutscher und englischer Dokumentation, Ankern und Vertragstests. | `tests/test_metadata.py` Verifikation |

## Funktionen im Detail

### Suchprofile

- Gruppenbasierte Strukturierung
- Drag&Drop zwischen Gruppen
- Profilspezifische Einstellungen
- Datumsfilter je Lauf

### Konvertierung

- Word nach PDF über Windows `win32com` mit `docx2pdf` als unabhängigem Fallback
- TXT nach PDF über `reportlab`
- Bilder nach PDF über Pillow
- OCR für gescannte PDFs ohne Textebene

### Scheduler & Auto-Kategorisierung

- Wiederkehrende Läufe von 15 Minuten bis 24 Stunden
- Läufe werden übersprungen, wenn bereits ein Scan aktiv ist
- Batch-Verarbeitung gruppiert aktive Profile nach Konten
- Regelbasierte Kategorisierung für Rechnungen, Versand, Verträge, Kündigungen, Steuern, Versicherungen, Bewerbungen und Bankdokumente

### Duplikate-Erkennung

- SHA-256-Hash-Prüfung
- Pro Profil konfigurierbar

<a name="installation--einrichtung"></a>
## Installation & Einrichtung

### Voraussetzungen

- Python 3.8+
- Microsoft Word für Word-nach-PDF-Konvertierung über `win32com` auf Windows,
  oder `docx2pdf` falls verfügbar
- Optional: Tesseract OCR
- Optional: Poppler

### Einrichtung

```bash
pip install -r requirements.txt
```

### Optional: Poppler

1. Download: <https://github.com/oschwartz10612/poppler-windows/releases>
2. Nach `C:\Program Files\poppler\` entpacken
3. Bei Bedarf `POPPLER_PATH` in `UniversalDocsGrabberV1.py` anpassen

### Optional: Tesseract

1. Download: <https://github.com/UB-Mannheim/tesseract/wiki>
2. Installation nach `C:\Program Files\Tesseract-OCR\`
3. Zu `PATH` hinzufügen

## Start

```bash
python UniversalDocsGrabberV1.py
```

oder Doppelklick auf `START.bat`.

## Typischer Arbeitsablauf

1. IMAP-Konto im Tab `Konten` anlegen
2. Suchprofil mit Gruppe, Filtern und Zielordner erstellen
3. Zeitraum einstellen
4. Einzelnes Profil oder alle aktiven Profile mit `START` ausführen
5. Ergebnisse im Tab `Dokumente` prüfen
6. Über `Einstellungen -> Companion-Export -> Redigierten Export speichern...` einen Bibliotheks-Snapshot erzeugen
7. Optional `web_companion/index.html` oder `?demo=1` öffnen, um den Export lokal im Browser-Companion zu prüfen

<a name="datenschutzmodell"></a>
## Datenschutzmodell & Lokale Daten

UniversalDocsGrabber läuft lokal auf Ihrem Rechner. Mail-Zugangsdaten werden über den Betriebssystem-Schlüsselspeicher abgelegt, Metadaten im Benutzerprofil. Es gibt keine Telemetrie, keine Cloud-Synchronisation und kein Backend.

- `%USERPROFILE%\.univ_docs_grabber\config_v1.json`
- `%USERPROFILE%\.univ_docs_grabber\documents.json`
- `%USERPROFILE%\Downloads\UnivDocs\`

Diese Dateien werden von Git ignoriert, da sie Kontonamen, lokale Pfade, Dokumentmetadaten und heruntergeladene Dokumente enthalten können.

<a name="plattform-strategie"></a>
## Plattform-Strategie & Web/PWA-Begleiter

Die Windows-Desktop-App bleibt die Vollversion für IMAP-Zugriff, OCR,
Konvertierung, Scheduling und lokale Dateiablage. Für macOS und Linux existiert
eine Source-Smoke-Abdeckung. Web, Android und iOS nutzen den lokalen
PWA-Companion in `web_companion/` auf Basis eines redigierten
`docsgrabber-library-v1.json`-Exports statt eines nativen Mail-Clients.

Der Export enthält Profile, Kategorien, Dokumentmetadaten, Profilstatistiken
und redigierte Pfadhinweise, aber keine Credentials, Dokumenttexte oder
PDF-Inhalte.

Siehe [EXPORTFORMAT.md](EXPORTFORMAT.md).

Der aktuelle Companion unterstützt lokalen Import, Suche, Profil- und
Kategorieübersicht, Dokument-Statusfilter und eine PWA-fähige Offline-Shell.
Manifest-, Service-Worker- und iOS-Anforderungen sind durch Node-Tests
abgedeckt; die eigentliche Installation und der Offline-Start auf Android/iOS
bleiben eine separate Prüfung auf realen Geräten oder Emulatoren.

Der Datenaustausch ist bewusst einseitig: Der Desktop erzeugt den redigierten
Export, der Companion liest ihn lokal. Es gibt keinen Rückimport und keinen
Cloud-Sync.

Der Companion lässt sich lokal über `web_companion/index.html?demo=1` mit einer
Demo-Bibliothek öffnen oder über einen einfachen lokalen HTTP-Server für
PWA-Tests bereitstellen.

Source-Smoke-Abdeckung für macOS/Linux wird in
`tests/source_platform_smoke.py` und `.github/workflows/source-platform-smoke.yml`
nachgehalten. Sie prüft den Offscreen-Start, Config-Roundtrips im temporären
Verzeichnis, sauberes Verhalten ohne Office-Konverter, den `docx2pdf`-Fallback
ohne `win32com` und klare Statusmeldungen bei fehlendem Tesseract/Poppler.

## Entwicklung

```bash
python tests/source_platform_smoke.py
python -m pytest -q
python -m py_compile UniversalDocsGrabberV1.py
```

## Ökosystem & Geschwister-Tools

UniversalDocsGrabber ist Teil der Dokumenten- und Desktop-Ökosysteme von
[doc-bricks](https://github.com/doc-bricks) und [open-bricks](https://github.com/open-bricks):

### doc-bricks — Dokument- & Mail-Werkzeuge
| Werkzeug | Beschreibung |
|---|---|
| [MailProcessor](https://github.com/doc-bricks/MailProcessor) | System-Tray-Starter und Orchestrator für alle Universal Mail Tools |
| [UniversalMailCleaner](https://github.com/doc-bricks/UniversalMailCleaner) | Regelbasierte IMAP-Postfachbereinigung mit sicherem Vorschaumodus |
| [UniversalInvoiceMail](https://github.com/doc-bricks/UniversalInvoiceMail) | Extraktion von Rechnungen, Belegen und Finanzdokumenten |
| [CleanMarkdown](https://github.com/doc-bricks/CleanMarkdown) | Markdown-Hygiene, Dialekt-Linting und AST-Bereinigung |
| [PDFtoPDFocr](https://github.com/doc-bricks/PDFtoPDFocr) | Batch-OCR-Werkzeug zur Ergänzung von Textebenen in gescannten PDFs |
| [MediaBrain](https://github.com/doc-bricks/MediaBrain) | Lokale Medienorganisation und Metadatenextraktion |

### file-bricks & dev-bricks — Desktop- & Entwickler-Werkzeuge
| Werkzeug | Beschreibung |
|---|---|
| [WinStorePackager](https://github.com/file-bricks/WinStorePackager) | MSIX-Paketierung und Bereitstellung für den Windows Store |
| [ProFiler](https://github.com/file-bricks/ProFiler) | Schnelle Datei-Suche nach mehreren Kriterien mit Duplikaterkennung |
| [ExplorerPro](https://github.com/file-bricks/ExplorerPro) | Lokaler Zwei-Fenster-Dateimanager für Windows |
| [DevCenter](https://github.com/dev-bricks/DevCenter) | Entwickler-Hub und Befehlsstarter |
| [WikiStub-Seed](https://github.com/dev-bricks/WikiStub-Seed) | Markdown-Wiki-Strukturierung und Stub-Generierung |

### ellmos-ai — Autonome Agenten- & MCP-Infrastruktur
| Werkzeug | Beschreibung |
|---|---|
| [ellmos-filecommander-mcp](https://github.com/ellmos-ai/ellmos-filecommander-mcp) | 47-Tool MCP-Server für lokale Dateisystem-Operationen, OCR und Papierkorb-Routing |
| [ellmos-codecommander-mcp](https://github.com/ellmos-ai/ellmos-codecommander-mcp) | Code-Intelligenz, AST-Refactorings, JSON-Korrektur und strukturelle Editierung |
| [n8n-manager-mcp](https://github.com/ellmos-ai/n8n-manager-mcp) | Workflow-Orchestrierung, Zugangsdaten-Governance und Lifecycle-Management |
| [system-explorer](https://github.com/ellmos-ai/system-explorer) | Nachweisorientierte Autoritätsauflösung und Schemaprüfung |
| [workflowhooker-provenance](https://github.com/ellmos-ai/workflowhooker-provenance) | Agentische Pre-Execution Briefings, Scope-Guards und Closing-Gates |
| [lock-master](https://github.com/ellmos-ai/lock-master) | Multi-Agenten-Sperren, Dateiansprüche und Schlichtung |
| [build-your-users-mind](https://github.com/ellmos-ai/build-your-users-mind) | Lokales Benutzerpräferenzmodell und kognitiver Zustandstracker |

## Drittanbieter-Lizenzen & Transparenz

UniversalDocsGrabber baut auf permissiven Open-Source-Komponenten auf:
- Die Anwendung selbst unterliegt der [MIT-Lizenz](LICENSE).
- Direkte Laufzeitabhängigkeiten (pypdf, reportlab, Pillow, xhtml2pdf, keyring, pytesseract, pdf2image, pywin32, docx2pdf) nutzen zulässige Open-Source-Lizenzen (MIT, BSD, Apache-2.0, PSF).
- PySide6 ist unter der LGPL-3.0 dynamisch verlinkt; Endanwender behalten gemäß LGPLv3 §4 die Freiheit zum Austausch der Qt-Bibliotheken.
- Die vollständige Konformitätsprüfung und Upstream-Quellen stehen in [THIRD_PARTY_LICENSES.md](THIRD_PARTY_LICENSES.md).

## Marketing & Zielgruppen

UniversalDocsGrabber adressiert vier zentrale Nutzergruppen:
1. **Solo-Unternehmer & Buchhaltungsfachkräfte**: Automatisierter Download wiederkehrender Rechnungen und Belege aus mehreren Postfächern in sortierte Ordner.
2. **Rechts-, Steuer- & Compliance-Assistenzen**: Vollständige lokale Datenhaltung vertraulicher Verträge und Mandantendokumente ohne Cloud-Transfer.
3. **Datenschutzbewusste Power-User & Archivare**: Lokaler Dokumentenindex mit schneller Suche und mobiler Offline-Prüfung über den PWA-Begleiter.
4. **Local-First KI- & Automations-Entwickler**: Sichere JSON-Metadatenschemata (`docsgrabber-library-v1.json`) ohne Offenlegung von Zugangsdaten oder rohen PDF-Binärdaten.

Ausführliche Suchbegriff-Cluster, Konkurrenzvergleiche und Roadmaps stehen in [MARKETING-LOG.txt](MARKETING-LOG.txt).

## Bekannte Einschränkungen

- OCR erfordert Tesseract und Poppler
- Word-Konvertierung setzt Microsoft Word über Windows `win32com` oder
  `docx2pdf` voraus; fehlt beides, wird die Konvertierung mit einer klaren
  Meldung übersprungen
- Für macOS/Linux ist bisher kein LibreOffice-basierter Fallback implementiert
- Die Suche ist konservativ ausgelegt und begrenzt die Mailanzahl pro Profil

## Suchbegriffe & Auffindbarkeit

`email attachment downloader`, `IMAP document downloader`, `Gmail attachment
archive`, `invoice email extraction`, `local-first document management`,
`Windows OCR document organizer`, `PySide6 mail tool`, `offline PWA document
review`.

## Suche & Eindeutigkeit

Verwenden Sie bei der Suche den genauen Projektnamen **UniversalDocsGrabber**
oder den Repository-Pfad `doc-bricks/UniversalDocsGrabber`. Das Projekt ist ein
lokaler E-Mail-Dokumenten-Downloader mit PWA-Begleiter — kein generischer
Dokumentenbetrachter, kein RAG-Parser, kein Cloud-OCR-Dienst und kein
Dokumentationsgenerator.

Maschinenlesbarer Kontext für Crawler und KI-Tools steht in [llms.txt](llms.txt).

## Lizenz

[MIT](LICENSE) - Lukas Geiger