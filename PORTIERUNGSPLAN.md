# Portierungsplan UniversalDocsGrabber

Readback: 2026-11-05 (Tier-2 6-Sprachen-Harmonisierung TW-UDG-02)

Readback-Basis: `master` bei Version 1.1.7;
Dieser Plan beschreibt den belegten Status und ist kein Geräte-, Store- oder
Native-Akzeptanzprotokoll.

## Statusmatrix

| Ziel | Belegter Status | Offener Nachweis / Grenze |
|---|---|---|
| Windows-Desktop | Vollversion; 65/65 Pytest-Tests bestanden, darin 3/3 Source-Smoke-Checks (247+ Gesamtsuite 100% grün) | Optionale OCR-/Poppler-/Word-Komponenten bleiben lokale Voraussetzungen |
| macOS/Linux | Source-/Offscreen-Vertrag geprüft (3 Checks) | Kein nativer Installer, kein Tray-/Autostart-Signoff und kein LibreOffice-Fallback; siehe `LIBREOFFICE_FALLBACK_EVAL.md` |
| Web/PWA-Companion | Lokaler statischer Companion mit Tier-2 6-Sprachen-Wörterbuch (DE, EN, ES, ZH, JA, RU); 32/32 Node-Smokes & 6/6 Pytest-Tests bestanden | Liest ausschließlich den redigierten Export; kein IMAP-Abruf, kein Upload und keine öffentliche Web-App |
| Rückimport / Cloud-Sync | Nicht implementiert und Nicht-Ziel des aktuellen Vertrags | Der Desktop erzeugt den Export, der Companion liest ihn lokal; kein Zurückschreiben und kein Cloud-Sync |
| Android/iOS | PWA-Quellverträge statisch geprüft; Tier-2 Sprachauswahl | Installation, Offline-Start und Lesbarkeit auf echtem Gerät/Emulator bleiben offen; keine native Voll-App |
| Windows Store | Vorkonfiguriert & Tier-2 harmonisiert (TW-UDG-01 & TW-UDG-02); Manifest, store_package.json und Staging in 6 Sprachen, 51/51 Preflight-Checks grün | MSIX-Build/WACK als separates Packaging-Gate dokumentiert (siehe `WINDOWS_STORE_PREP.md`); Partner Center Upload erfordert Nutzerfreigabe |

## Export- und Datenschutzvertrag

`docsgrabber-library-v1.json` enthält nur redigierte Profile, Kategorien,
Dokumentmetadaten, Pfadhinweise und Laufstatus. Credentials, Tokens,
Mail-Body-Volltexte, PDF-Inhalte und schreibende Desktop-Änderungen bleiben
außerhalb des Formats. Maßgebliche Details stehen in `EXPORTFORMAT.md` und
`web_companion/README.md`.

## Prüfstand

Der aktuelle Readback wurde im kanonischen Plan-D-Checkout mit
`python -B -m pytest -p no:cacheprovider -ra`,
`python -B tests/source_platform_smoke.py`,
`python scripts/check_store_readiness.py` und
`node --test web_companion/tests/library.test.mjs web_companion/tests/pwa_smoke.test.mjs`
ausgeführt. Geräte-/Emulator-, native-, Store- und Upload-/Sync-Aussagen dürfen
erst nach einem jeweils passenden externen Nachweis ergänzt werden.
