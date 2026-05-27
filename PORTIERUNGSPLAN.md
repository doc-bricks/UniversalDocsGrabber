# Portierungsplan UniversalDocsGrabber

Stand: 2026-05-27

## Kurzentscheidung

UniversalDocsGrabber bleibt zuerst eine lokale Desktop-Anwendung. Die Kernfunktion
ist das regelbasierte Abrufen, Konvertieren, OCR-Verarbeiten und Ablegen von
Dokumenten aus IMAP-Postfächern. Dafür braucht die App lokale Zugangsdaten,
Dateisystemzugriff, optionale Tesseract-/Poppler-Installationen und unter Windows
teilweise Office-/COM-Konvertierung. Eine direkte Android- oder iOS-Kopie wäre
deshalb fachlich und technisch zu schwergewichtig.

Der sinnvolle plattformübergreifende Weg ist:

1. Windows-Desktop bleibt die Vollversion.
2. macOS und Linux werden als Source-/Smoke-Ziele geprüft, aber ohne Anspruch auf
   vollständige Office-Konvertierung im ersten Schritt.
3. Web, Android und iOS laufen später über einen Web/PWA-Companion, der redigierte
   Profil- und Dokumentmetadaten nutzt, nicht über IMAP-Credentials im Browser.

## Warum Portierung sinnvoll ist

- Nutzer wollen Dokumentfunde, Profilregeln und Ablageergebnisse auch außerhalb
  des Hauptrechners prüfen.
- Dokumenten-Workflows sind mobil relevant: unterwegs kontrollieren, ob wichtige
  Anhänge eingegangen sind, ohne das Mailkonto erneut in einer Mobile-App
  einzurichten.
- Eine Web/PWA-Oberfläche kann Profile, Kategorien und Metadaten erklären, ohne
  lokale Zugangsdaten, PDFs oder private Mailinhalte hochzuladen.
- macOS/Linux-Smokes reduzieren Windows-Lock-in für Open-Source-Nutzer, auch wenn
  einzelne Konverter plattformspezifisch bleiben.

## Plattformabwägung

| Option | Entscheidung | Begründung |
|---|---|---|
| Windows Store | Vorgemerkt, nicht P0 | Technisch passend für die Desktop-App, aber erst nach Store-Privacy-Texten, Support-URL, Runtime-Bündelung für Tesseract/Poppler und Credential-Prüfung. |
| Android-Version | Kein nativer Clone | Hintergrund-IMAP, Dateisystemzugriff und OCR/Office-Konvertierung passen schlecht zu einer nativen Mobile-Kopie. Android nur als PWA-Companion. |
| Webapp | Bevorzugte Companion-Linie | Redigierte Profile, Kategorien, Dokumentindex und Laufstatus können browserfähig werden. Kein öffentlicher Upload privater Maildaten. |
| iOS-Version | Kein nativer Clone | iOS-Sandbox und Hintergrundlimits sprechen gegen einen vollständigen Mail-Grabber. iOS nur als PWA-Companion oder später als sehr dünne Hülle. |
| Mac App | P2 Source-Smoke | IMAP, PDF-Index und Teile der Konvertierung sind möglich; Windows-COM entfällt, Tesseract/Poppler müssen separat geprüft werden. |
| Linux-Version | P2 Source-Smoke | IMAP, PDF-Index und OCR sind plausibel; Office-Konvertierung läuft über LibreOffice statt COM. Packaging erst nach erfolgreichem Smoke. |

## Zielarchitektur

### Desktop-Vollversion

- PySide6-App mit lokaler Konfiguration unter `%USERPROFILE%\.univ_docs_grabber`.
- Mail-Credentials bleiben im Betriebssystem-Keyring.
- Downloads und PDFs bleiben auf dem lokalen Dateisystem.
- Windows bleibt Referenzplattform, weil Word-Konvertierung und vorhandene
  Nutzerpfade dort am stabilsten sind.

### Austauschformat

Geplant ist `docsgrabber-library-v1.json` als redigierter Export:

- Suchprofile, Kategorien und Scheduler-Metadaten
- Dokumentindex ohne Mail-Passwörter und ohne Volltext aus Mailbodys
- relative oder bewusst redigierte Zielpfade
- Statistiken pro Profil und letzter Laufstatus
- keine heruntergeladenen PDFs, keine Credentials, keine Tokens

Details stehen in `EXPORTFORMAT.md`.

### Web/PWA-Companion

Der Companion soll zunächst nur lokale Exporte anzeigen und bearbeiten:

- Profil- und Kategorienübersicht
- Dokumentindex mit Such- und Filteransicht
- Import/Export von `docsgrabber-library-v1.json`
- mobile Ansicht für Kontrolle, nicht für automatisches Mail-Abrufen

## Umsetzungsschritte

### P0: Desktop-Exportvertrag

- `docsgrabber-library-v1.json` final spezifizieren.
- Exportfunktion für Profile, Kategorien und Dokumentindex ergänzen.
- Importpfad nur für redigierte Profile prüfen; Credentials bleiben manuell.

### P1: Web/PWA-Prototyp

- `web_companion/` als statischen Companion vorbereiten.
- JSON-Import, Suche und Kategorienfilter umsetzen.
- Mobile Layouts für Android und iOS testen.

### P2: macOS/Linux-Smokes

- Start auf macOS und Linux ohne Windows-COM prüfen.
- Tesseract-/Poppler-Erkennung plattformneutral dokumentieren.
- Fallback für Office-Konvertierung über LibreOffice bewerten.

### P3: Store- und Mobile-Distribution

- Windows-Store-Readiness erst nach Privacy-/Support-URL, Store-Listing,
  Runtime-Bündelung und WACK prüfen.
- Android/iOS bleiben PWA-Testziele. Native Hüllen erst, wenn der Companion
  nachweislich genutzt wird.

## Nicht-Ziele

- Keine öffentliche Webapp, die Mailzugänge oder Dokumentinhalte hochlädt.
- Keine native Mobile-App mit vollständigem IMAP-Scheduler.
- Kein automatischer Cloud-Sync privater Dokumente.
- Keine Store-Einreichung vor sauberem Datenschutz- und Support-Pfad.
