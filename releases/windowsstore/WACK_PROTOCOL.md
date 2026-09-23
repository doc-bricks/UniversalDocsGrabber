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

## Durchgeführte Läufe

### Preflight-Prüfung 2026-09-23

- Datum: 2026-09-23
- MSIX-Pfad: `releases\windowsstore\UniversalDocsGrabber.msix` (Preflight-Staging)
- WACK-Gesamtergebnis: PASS
- Anzahl PASS: 6 (AppManifest, SecurityFeatures, SupportedAPIs, PackageCompliance, PerformanceAndResources, CleanUninstall)
- Anzahl FAIL: 0
- Anzahl WARNING: 0
- Relevante Findings: Keine. Manifest, Identität `Geiger.UniversalDocsGrabber`, Publisher `CN=52596601-BAB4-4F3F-B182-E8F3F273B202`, Version 1.1.7.0, Capabilities `runFullTrust` + `internetClient` und Kacheln (inkl. StoreLogo 50x50) vollständig konsistent.
- Tooling: `scripts\run_windows_wack.py`
- Report-Dateien: `releases\windowsstore\test_reports\wack_preflight_20260923.xml` / `.json`

## Eintrag für den nächsten Lauf

- Datum:
- MSIX-Pfad:
- WACK-Gesamtergebnis:
- Anzahl PASS:
- Anzahl FAIL:
- Anzahl WARNING:
- Relevante Findings:
- Nächste Korrektur:
