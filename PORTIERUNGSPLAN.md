# Portierungsplan UniversalDocsGrabber

Readback: 2026-08-12

Maßgeblicher Remote-Stand: `master` bei `2f4ec009dd6035c757a305606fb58f9328f3b96e`.
Dieser Plan beschreibt den belegten Status und ist kein Geräte-, Store- oder
Native-Akzeptanzprotokoll.

## Statusmatrix

| Ziel | Belegter Status | Offener Nachweis / Grenze |
|---|---|---|
| Windows-Desktop | Vollversion; 53/53 Pytest-Tests und 3/3 Source-Smoke-Checks bestanden | Optionale OCR-/Poppler-/Word-Komponenten bleiben lokale Voraussetzungen |
| macOS/Linux | Source-/Offscreen-Vertrag geprüft (3 Checks) | Kein nativer Installer, kein Tray-/Autostart-Signoff und kein LibreOffice-Fallback; siehe `LIBREOFFICE_FALLBACK_EVAL.md` |
| Web/PWA-Companion | Lokaler statischer Companion; 32/32 Node-Smokes bestanden | Liest ausschließlich den redigierten Export; kein IMAP-Abruf, kein Upload und keine öffentliche Web-App |
| Rückimport / Cloud-Sync | Nicht implementiert und Nicht-Ziel des aktuellen Vertrags | Der Desktop erzeugt den Export, der Companion liest ihn lokal; kein Zurückschreiben und kein Cloud-Sync |
| Android/iOS | PWA-Quellverträge statisch geprüft | Installation, Offline-Start und Lesbarkeit auf echtem Gerät/Emulator bleiben offen; keine native Voll-App |
| Windows Store | Separates, nicht ausgeführtes Release-Gate | Kein MSIX/WACK/Partner-Center-Nachweis in diesem Readback; Store-Entscheidung bleibt getrennt |

## Export- und Datenschutzvertrag

`docsgrabber-library-v1.json` enthält nur redigierte Profile, Kategorien,
Dokumentmetadaten, Pfadhinweise und Laufstatus. Credentials, Tokens,
Mail-Body-Volltexte, PDF-Inhalte und schreibende Desktop-Änderungen bleiben
außerhalb des Formats. Maßgebliche Details stehen in `EXPORTFORMAT.md` und
`web_companion/README.md`.

## Prüfstand

Der aktuelle Readback wurde im frischen Remote-Checkout mit
`python -B -m pytest -p no:cacheprovider -ra`,
`python -B tests/source_platform_smoke.py` und
`node --test web_companion/tests/library.test.mjs web_companion/tests/pwa_smoke.test.mjs`
ausgeführt. Geräte-/Emulator-, native-, Store- und Upload-/Sync-Aussagen dürfen
erst nach einem jeweils passenden externen Nachweis ergänzt werden.
