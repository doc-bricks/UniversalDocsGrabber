# Exportformat `docsgrabber-library-v1.json`

Stand: 2026-05-27

Dieses Dokument beschreibt den umgesetzten Austauschvertrag für Desktop, Web/PWA
und spätere Plattform-Smokes. Das Format ist bewusst redigiert: Es transportiert
Profile, Kategorien, Dokumentmetadaten und Laufstatus, aber keine Mailzugänge,
Tokens, Passwörter oder heruntergeladenen Dokumentinhalte.

## Zweck

`docsgrabber-library-v1.json` soll UniversalDocsGrabber für mobile und
browserbasierte Companion-Oberflächen nutzbar machen. Der Desktop bleibt die
autoritative Vollversion für IMAP, OCR, Konvertierung und Dateisystemzugriff.

## Struktur

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
  "base_path_hint": {
    "kind": "basename",
    "value": "UnivDocs"
  },
  "accounts": [],
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
- Dokumenteinträge enthalten keine Absender- oder Betreff-Volltexte.
- Dokumente erhalten nur Metadaten wie Dateiname, Typ, Hash, Kategorie,
  Profilreferenz, Datum und optional einen Missing-/Available-Status.

## Mindestfelder für Companion-Nutzung

- Profile: Name, Gruppe, aktive Filter, Zielkategorie, Auto-Kategorisierung.
- Kategorien: Name, Regelquelle, Beschreibung.
- Dokumente: Titel/Dateiname, Kategorie, Profil, Datum, Dateityp, Hash,
  redigierter Pfadhinweis.
- Laufstatus: letzter Export, letzter Scan pro Profil, Anzahl gefundener
  Dokumente und Fehlerhinweise ohne Credentials.

## Aktuell exportierte Felder

- `accounts`: redigierte `account-<hash>`-Referenzen plus Anzahl verknüpfter Profile
- `profiles`: ID, Name, Gruppe, Aktiv-Status, `account_ref`, Zielordner, Filter und effektive Download-/Auto-Kategorisierungs-Einstellungen
- `categories`: zusammengeführt aus globalen Regeln, Profil-Overrides und erkannten Dokumentpfaden
- `documents`: Profilname, Dateiname, Datum, Typ, Kategorie, `path_hint`, Status und optionale SHA-256 bei vorhandener lokaler Datei
- `run_summary`: Anzahl exportierter Profile/Dokumente, aktiver Profile, Scheduler-Intervall und Profilstatistiken

## Desktop-Auslöser

Der Export wird direkt in der Desktop-App über
`Einstellungen -> Companion-Export -> Redigierten Export speichern...`
ausgelöst.

## Kompatibilitätsregeln

- Neue Felder sind optional.
- Importer ignorieren unbekannte Felder.
- `schema` und `schema_version` sind Pflicht.
- Schreibende Versionen müssen UTF-8 ohne BOM verwenden.
- Endnutzertexte im deutschen Companion verwenden echte Umlaute.
