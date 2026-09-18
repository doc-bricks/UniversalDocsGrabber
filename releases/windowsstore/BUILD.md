# UniversalDocsGrabber - Windows Store Build-Anleitung

## Voraussetzungen

1. Python 3.10+ mit PySide6
2. PyInstaller für den Desktop-Build
3. Windows SDK mit `makeappx.exe` und `appcert.exe` (WACK)
4. Lokaler Schreibpfad außerhalb eines synchronisierten Ordners für große MSIX-Artefakte, z. B. `C:\build\universaldocsgrabber-store`

Die Befehle verwenden bewusst Platzhalter statt personenbezogener Arbeitsverzeichnisse.
Setze `$projectRoot` auf den lokalen UniversalDocsGrabber-Checkout und `$softwareRoot` auf den
lokalen `.SOFTWARE`-Pipelineordner, der die zentralen Store-Skripte enthält.

## Schritt 0: Store-Material aktualisieren

```powershell
$projectRoot = "C:\path\to\UniversalDocsGrabber"
Set-Location $projectRoot
$env:PYTHONIOENCODING="utf-8"
python scripts/generate_store_assets.py
```

Erzeugt:

- `store_assets\Square44x44Logo.png`
- `store_assets\Square50x50Logo.png` (StoreLogo)
- `store_assets\Square150x150Logo.png`
- `store_assets\Wide310x150Logo.png`
- `store_assets\Square310x310Logo.png`
- `releases\windowsstore\screenshots\shot-1-inbox-and-rules.png`
- `releases\windowsstore\screenshots\shot-2-document-extraction.png`
- `releases\windowsstore\screenshots\shot-3-ocr-and-conversion.png`
- `releases\windowsstore\screenshots\shot-4-companion-export.png`
- `releases\windowsstore\StoreLogo.png`

## Schritt 1: Desktop-EXE bauen

```powershell
Set-Location $projectRoot
pyinstaller --noconfirm --onedir --windowed --name "UniversalDocsGrabber" --icon "UniversalDocsGrabber_icon.ico" run.py
```

Erwarteter Hauptpfad:

- `dist\UniversalDocsGrabber\UniversalDocsGrabber.exe`

## Schritt 2: Store-Pretest

```powershell
$softwareRoot = "C:\path\to\.SOFTWARE"
& (Join-Path $softwareRoot "_STORE\msstore_pretest.ps1") `
  -ExePath (Join-Path $projectRoot "dist\UniversalDocsGrabber\UniversalDocsGrabber.exe") `
  -ProjectRoot $projectRoot `
  -StartWait 8
```

## Schritt 3: MSIX lokal außerhalb von OneDrive bauen

```powershell
$outputRoot = "C:\build\universaldocsgrabber-store"
& (Join-Path $softwareRoot "_STORE\msstore_build_msix.ps1") `
  -ProjectRoot $projectRoot `
  -ExePath (Join-Path $projectRoot "dist\UniversalDocsGrabber\UniversalDocsGrabber.exe") `
  -OutputMsix (Join-Path $outputRoot "UniversalDocsGrabber.msix")
```

## Schritt 4: WACK als Administrator

```powershell
$reportRoot = Join-Path $projectRoot "releases\windowsstore\test_reports"
Start-Process powershell -Verb RunAs -ArgumentList @(
  "-ExecutionPolicy Bypass",
  "-File $(Join-Path $softwareRoot '_STORE\msstore_wack.ps1')",
  "-MsixPath $(Join-Path $outputRoot 'UniversalDocsGrabber.msix')",
  "-ReportDir $reportRoot"
)
```

Die Ergebnisse danach in `releases\windowsstore\WACK_PROTOCOL.md` eintragen.
