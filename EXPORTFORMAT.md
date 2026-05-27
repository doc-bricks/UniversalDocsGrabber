# Exportformat `docsgrabber-library-v1.json`

Stand: 2026-05-27

Dieses Dokument beschreibt den geplanten Austauschvertrag für Desktop, Web/PWA
und spätere Plattform-Smokes. Das Format ist bewusst redigiert: Es transportiert
Profile, Kategorien, Dokumentmetadaten und Laufstatus, aber keine Mailzugänge,
Tokens, Passwörter oder heruntergeladenen Dokumentinhalte.

## Zweck

`docsgrabber-library-v1.json` soll UniversalDocsGrabber für mobile und
browserbasierte Companion-Oberflächen nutzbar machen. Der Desktop bleibt die
autoritative Vollversion für IMAP, OCR, Konvertierung und Dateisystemzugriff.

## Geplante Struktur

```json
{
  "schema": "docsgrabber-library",
  "schema_version": "1.0",
  "app": {
    "name": "UniversalDocsGrabber",
    "version": "1.x",
    "exported_at": "2026-05-27T12:00:00+02:00"
  },
  "capabilities": {
    "redacted": true,
    "contains_credentials": false,
    "contains_document_files": false,
    "contains_mail_body_text": false
  },
  "profiles": [],
  "categories": [],
  "documents": [],
  "run_summary": {}
}
```

## Datenschutzregeln

- `accounts` dürfen nur Anzeigenamen oder redigierte IDs enthalten.
- Passwörter, OAuth-Tokens, Server-Passwörter und Keyring-Referenzen werden nie
  exportiert.
- Lokale absolute Pfade werden standardmäßig redigiert oder relativ zum
  gewählten Exportwurzelordner geschrieben.
- Mail-Body-Volltexte und PDF-Inhalte bleiben außerhalb des Formats.
- Dokumente erhalten nur Metadaten wie Dateiname, Typ, Hash, Kategorie,
  Profilreferenz, Datum und optional einen Missing-/Available-Status.

## Mindestfelder für Companion-Nutzung

- Profile: Name, Gruppe, aktive Filter, Zielkategorie, Auto-Kategorisierung.
- Kategorien: Name, Regelquelle, Beschreibung.
- Dokumente: Titel/Dateiname, Kategorie, Profil, Datum, Dateityp, Hash,
  redigierter Pfadhinweis.
- Laufstatus: letzter Export, letzter Scan pro Profil, Anzahl gefundener
  Dokumente und Fehlerhinweise ohne Credentials.

## Kompatibilitätsregeln

- Neue Felder sind optional.
- Importer ignorieren unbekannte Felder.
- `schema` und `schema_version` sind Pflicht.
- Schreibende Versionen müssen UTF-8 ohne BOM verwenden.
- Endnutzertexte im deutschen Companion verwenden echte Umlaute.
