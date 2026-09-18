# UniversalDocsGrabber - WACK-Protokoll

## Ziel

Nach dem lokalen MSIX-Build soll der Windows App Certification Kit-Lauf dokumentiert werden, damit Store-Submission und spätere Regressionen nachvollziehbar bleiben.

## Vorbereiteter Befehl

```powershell
$projectRoot = "C:\path\to\UniversalDocsGrabber"
$softwareRoot = "C:\path\to\.SOFTWARE"
$outputRoot = "C:\build\universaldocsgrabber-store"
$reportRoot = Join-Path $projectRoot "releases\windowsstore\test_reports"
Start-Process powershell -Verb RunAs -ArgumentList @(
  "-ExecutionPolicy Bypass",
  "-File $(Join-Path $softwareRoot '_STORE\msstore_wack.ps1')",
  "-MsixPath $(Join-Path $outputRoot 'UniversalDocsGrabber.msix')",
  "-ReportDir $reportRoot"
)
```

## Aktueller Status

- Stand dieses Laufs: Store-Packaging-Staging vollständig aufgebaut. Manifest, Icons, 1080p Screenshots und Metadaten validiert.
- Status: Bereit für Desktop-Build und anschließenden lokalen MSIX-Testlauf.
- Erwartete Ablage:
  - XML-Report unter `releases\windowsstore\test_reports\`
  - Konsolenlog unter `releases\windowsstore\test_reports\`

## Eintrag für den nächsten Lauf

- Datum:
- MSIX-Pfad:
- WACK-Gesamtergebnis:
- Anzahl PASS:
- Anzahl FAIL:
- Anzahl WARNING:
- Relevante Findings:
- Nächste Korrektur:
