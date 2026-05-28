# Web/PWA-Companion

Stand: 2026-05-28

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

## Aktuelle Funktionen

- Import von `docsgrabber-library-v1.json`
- Demo-Export über `?demo=1` oder den Demo-Button
- Profil-, Kategorien- und Dokumentindex-Ansicht
- Suchfeld sowie Filter für Profil, Kategorie und Status
- Dokumentdetailansicht mit Pfadhinweis, Datum, Dateityp, Status und SHA-256
- Offline-fähige statische PWA-Basis für Android-, iOS- und Web-Smokes

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
- Noch kein Rückimport bearbeiteter Profilmetadaten in die Desktop-App
