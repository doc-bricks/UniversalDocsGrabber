@echo off
setlocal EnableExtensions

cd /d "%~dp0"
set "PROJECT_ROOT=%CD%"
set "BUILD_ROOT=C:\_Local_DEV\codex_build\universaldocsgrabber"
set "VENV_DIR=%BUILD_ROOT%\.venv"
set "BUILD_PY=%VENV_DIR%\Scripts\python.exe"
set "DIST_DIR=%BUILD_ROOT%\dist"
set "WORK_DIR=%BUILD_ROOT%\work"
set "SPEC_DIR=%BUILD_ROOT%\spec"
set "SCANNER=%PROJECT_ROOT%\..\..\_tools\build_exclude_scanner.py"
set "EXCLUDES_FILE=%BUILD_ROOT%\pyinstaller-excludes.txt"
set "APP_NAME=UniversalDocsGrabber"
set "ENTRY_SCRIPT=%PROJECT_ROOT%\UniversalDocsGrabberV1.py"
set "ICON_FILE=%PROJECT_ROOT%\UniversalDocsGrabber_icon.ico"
set "PYTHONIOENCODING=utf-8"
set "PYTHONPATH="
set "QT_QPA_PLATFORM=offscreen"

python --version >nul 2>&1
if errorlevel 1 (
    echo [FEHLER] Python nicht gefunden!
    pause
    exit /b 1
)

if not exist "%BUILD_PY%" (
    echo [build] Erstelle lokales Build-venv: %VENV_DIR%
    py -3 -m venv "%VENV_DIR%"
    if errorlevel 1 (
        pause
        exit /b 1
    )
)

echo [build] Installiere Build-Abhaengigkeiten...
"%BUILD_PY%" -m pip install --disable-pip-version-check --upgrade pip
if errorlevel 1 (
    pause
    exit /b 1
)
"%BUILD_PY%" -m pip install --disable-pip-version-check -r "%PROJECT_ROOT%\requirements.txt" pyinstaller
if errorlevel 1 (
    pause
    exit /b 1
)

echo [build] Syntax-Check
"%BUILD_PY%" -m py_compile "%ENTRY_SCRIPT%"
if errorlevel 1 (
    pause
    exit /b 1
)

if not exist "%BUILD_ROOT%" mkdir "%BUILD_ROOT%"
set "EXCLUDES="
if exist "%SCANNER%" (
    "%BUILD_PY%" "%SCANNER%" --project "%PROJECT_ROOT%" --emit pyinstaller > "%EXCLUDES_FILE%"
    if errorlevel 1 (
        pause
        exit /b 1
    )
    set /p EXCLUDES=<"%EXCLUDES_FILE%"
)

echo [build] Auto-Excludes: %EXCLUDES%

if exist "%PROJECT_ROOT%\dist\UniversalDocsGrabber_V1.exe" del /q "%PROJECT_ROOT%\dist\UniversalDocsGrabber_V1.exe"
if exist "%PROJECT_ROOT%\UniversalDocsGrabber_V1.exe" del /q "%PROJECT_ROOT%\UniversalDocsGrabber_V1.exe"

echo [build] PyInstaller
"%BUILD_PY%" -m PyInstaller --noconfirm --clean --windowed --onefile --noupx ^
  --name "%APP_NAME%" ^
  --icon "%ICON_FILE%" ^
  %EXCLUDES% ^
  --distpath "%DIST_DIR%" ^
  --workpath "%WORK_DIR%" ^
  --specpath "%SPEC_DIR%" ^
  "%ENTRY_SCRIPT%"
if errorlevel 1 (
    pause
    exit /b 1
)

if not exist "%PROJECT_ROOT%\dist" mkdir "%PROJECT_ROOT%\dist"

copy /Y "%DIST_DIR%\%APP_NAME%.exe" "%PROJECT_ROOT%\dist\%APP_NAME%.exe" >nul
copy /Y "%DIST_DIR%\%APP_NAME%.exe" "%PROJECT_ROOT%\%APP_NAME%.exe" >nul

echo.
echo [build] OK -- dist\%APP_NAME%.exe
echo [build] Root-EXE: %APP_NAME%.exe
echo [build] Buildroot: %BUILD_ROOT%
endlocal
