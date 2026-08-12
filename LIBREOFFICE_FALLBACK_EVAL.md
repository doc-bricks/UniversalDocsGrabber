# LibreOffice-Fallback-Bewertung

Readback: 2026-08-12

Für macOS/Linux ist aktuell kein LibreOffice-basierter Office-zu-PDF-Fallback
implementiert oder abgenommen. Der bestehende Vertrag bleibt:

- Windows nutzt Microsoft Word über `win32com`, sofern vorhanden.
- `docx2pdf` bleibt ein unabhängiger Fallback, sofern installiert.
- Fehlt beides, meldet die Anwendung den kontrollierten Konverter-Abbruch.

Der Source-Smoke prüft den Start-, Config- und Exportvertrag ohne Windows-COM;
der Pytest-Regressionstest deckt den `docx2pdf`-Fallback ohne `win32com` ab.
Ein späterer LibreOffice-Slice benötigt belegte Nicht-Windows-Nachfrage,
isoliertes temporäres Profil, Timeout-/Exitcode-Behandlung sowie echte Office-
Fixtures auf macOS oder Linux. Bis dahin bleibt die Erweiterung deferred und
ist weder Store-, Geräte- noch Companion-Akzeptanz.
