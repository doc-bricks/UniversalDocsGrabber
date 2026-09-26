# -*- mode: python ; coding: utf-8 -*-
# PyInstaller spec file für UniversalDocsGrabber
# Build: python -m PyInstaller UniversalDocsGrabber.spec --clean --noconfirm

block_cipher = None

a = Analysis(
    ['UniversalDocsGrabberV1.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('assets', 'assets'),
        ('app_icon_loader.py', '.'),
    ],
    hiddenimports=[
        'PySide6.QtWidgets',
        'PySide6.QtGui',
        'PySide6.QtCore',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='UniversalDocsGrabber',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    icon='UniversalDocsGrabber_icon.ico',
)
