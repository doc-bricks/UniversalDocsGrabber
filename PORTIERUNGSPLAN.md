# Portierungsplan UniversalDocsGrabber

Stand: 2026-05-28

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
3. Web, Android und iOS laufen über einen Web/PWA-Companion, der redigierte
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

`docsgrabber-library-v1.json` ist jetzt als redigierter Export im Desktop
umgesetzt:

- Suchprofile, Kategorien und Scheduler-Metadaten
- Dokumentindex ohne Mail-Passwörter und ohne Volltext aus Mailbodys
- relative oder bewusst redigierte Zielpfade
- Statistiken pro Profil und letzter Laufstatus
- optionale SHA-256 nur für lokal vorhandene Dateien
- keine heruntergeladenen PDFs, keine Credentials, keine Tokens

Der Export lässt sich direkt in der App über
`Einstellungen -> Companion-Export -> Redigierten Export speichern...`
auslösen.

Details stehen in `EXPORTFORMAT.md`.

### Web/PWA-Companion

Der Companion ist jetzt als statischer lokaler P1-Prototyp umgesetzt:

- Import von `docsgrabber-library-v1.json` direkt im Browser
- Profil- und Kategorienübersicht
- Dokumentindex mit Such-, Profil-, Kategorien- und Statusfiltern
- Detailansicht für Pfadhinweise, Verfügbarkeit, Dateityp und Hash
- Demo-Load, Manifest und Service Worker für lokale PWA-/Offline-Smokes
- mobile Ansicht für Kontrolle, nicht für automatisches Mail-Abrufen

## Umsetzungsschritte

### P0: Desktop-Exportvertrag

- `docsgrabber-library-v1.json` final spezifizieren. (erledigt 2026-05-27)
- Exportfunktion für Profile, Kategorien und Dokumentindex ergänzen. (erledigt 2026-05-27)
- Importpfad nur für redigierte Profile prüfen; Credentials bleiben manuell. (offen für späteren Rückimport)

### P1: Web/PWA-Prototyp

- `web_companion/` als statischen Companion vorbereiten. (erledigt 2026-05-28)
- JSON-Import, Suche und Kategorienfilter umsetzen. (erledigt 2026-05-28)
- Mobile Layouts für Android und iOS testen. (offen für P2-Smokes)

### P2: PWA- und Desktop-Smokes

- Android-/iOS-PWA-Smokes für Installierbarkeit, Offline-Start und Lesbarkeit dokumentieren.
- Start auf macOS und Linux ohne Windows-COM prüfen. (erledigt 2026-06-05)
- Tesseract-/Poppler-Erkennung plattformneutral dokumentieren. (erledigt 2026-06-05)
- Fallback für Office-Konvertierung über LibreOffice bewerten. (als Folgeaufgabe offen)

Ergebnis 2026-06-05:

- `tests/source_platform_smoke.py` prüft jetzt reproduzierbar Offscreen-Start,
  temporäre Config-Persistenz, den nicht-Windows-sicheren Word-Pfad ohne
  `win32com` und die klare OCR-Rückmeldung bei fehlendem Tesseract/Poppler-Stack.
- `.github/workflows/source-platform-smoke.yml` führt denselben Smoke auf
  `ubuntu-latest` und `macos-latest` aus.
- Manuell verifiziert wurden drei Läufe: Windows lokal, Ubuntu 24.04 in WSL und
  macOS auf dem Mac Studio. Alle drei Smokes liefen grün.
- Bewertung: Die Desktop-App startet plattformneutral sauber für Config,
  Profilverwaltung und Exportvertrag. Die Office-Konvertierung bleibt derzeit
  bewusst Windows-zentriert; ein LibreOffice-Fallback ist fachlich möglich,
  aber noch kein belegter P0/P1-Bedarf.

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
