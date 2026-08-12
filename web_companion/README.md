# Web/PWA-Companion

Stand: 2026-08-12

Der Companion ist jetzt als statischer lokaler Web/PWA-Prototyp umgesetzt. Er
liest `docsgrabber-library-v1.json` direkt im Browser und zeigt Profile,
Kategorien, Dokumentmetadaten sowie redigierte Pfadhinweise an, ohne IMAP,
Passwörter oder Dokumentdateien in eine Webanwendung zu verlagern.

## Enthaltene Dateien

- `index.html` für den lokalen Einstieg
- `app.js` für Import, Filter und Detailansicht
- `library.js` für Schema-Validierung und Demo-Daten
- `app.css` für die mobile Oberfläche
- `manifest.webmanifest` und `sw.js` für PWA-/Offline-Basis
- `tests/library.test.mjs` für Parser- und Filter-Smokes
- `tests/pwa_smoke.test.mjs` für Manifest-, Service-Worker- und iOS-Quellverträge

## Aktuelle Funktionen

- Import von `docsgrabber-library-v1.json`
- Demo-Export über `?demo=1` oder den Demo-Button
- Profil-, Kategorien- und Dokumentindex-Ansicht
- Suchfeld sowie Filter für Profil, Kategorie und Status
- Dokumentdetailansicht mit Pfadhinweis, Datum, Dateityp, Status und SHA-256
- Offline-fähige statische PWA-Basis für Android, iOS und Web
- iOS-Quellhärtung mit `viewport-fit=cover`, Safe-Area-CSS und opakem Apple-Touch-Icon

## Verifizierter Status

- Der lokale, read-only Exportimport sowie Parser, Filter, Manifest und Service
  Worker sind durch Node-Tests abgesichert.
- Die iOS-spezifischen Quellanforderungen sind statisch getestet; das ist kein
  Nachweis einer Installation oder eines Offline-Starts auf einem iPhone/iPad.
- Android- und iOS-Geräte-Smokes für Installation, Offline-Start und Lesbarkeit
  bleiben offen, bis ein Gerät oder Emulator mit nachvollziehbarer Evidenz
  verfügbar ist.

## Start lokal

```bash
cd web_companion
python -m http.server 4176
```

Danach im Browser öffnen:

- `http://127.0.0.1:4176/index.html`
- `http://127.0.0.1:4176/index.html?demo=1`

## Grenzen

- Kein IMAP-Abruf im Browser
- Keine Speicherung von Passwörtern oder Tokens
- Kein Upload privater PDFs oder Mailtexte
- Kein Rückimport bearbeiteter Profilmetadaten in die Desktop-App: Der Austausch
  läuft bewusst nur vom Desktop zum Companion und erzeugt keinen Cloud-Sync.
