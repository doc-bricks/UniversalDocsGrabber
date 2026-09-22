# Third-Party License Inventory & Open-Source Compliance

**Project:** UniversalDocsGrabber (`doc-bricks/UniversalDocsGrabber`)<br>
**Audit Date:** 2026-09-22 (Re-audited during Pfad A Technical Hygiene; prior baseline 2026-09-14)<br>
**Project License:** [MIT](LICENSE) (Lukas Geiger) & [NOTICE](NOTICE)<br>
**Status:** 100% Permissive Open Source — Verified Zero Copyleft Contamination — 100% Local-First / Zero-Egress Compatible

---

## 1. Executive Summary & Compliance Declaration

UniversalDocsGrabber is an open-source, local-first email attachment downloader, document converter, and local archive manager. It processes confidential email streams, invoices, tax documents, and contracts locally on the user's workstation. 

To ensure complete legal compliance, organizational safety, and zero external privacy risks:
1. **100% Permissive / Weak Copyleft (LGPL-3.0 with dynamic linking)**: All direct runtime and build dependencies use OSI-approved permissive licenses (MIT, BSD-3-Clause, Apache-2.0, Python Software Foundation License) or LGPL-3.0 (Qt for Python/PySide6) dynamically linked in compliance with Section 4 of LGPLv3.
2. **Zero-Egress & Air-Gap Capable**: No runtime dependency establishes unsolicited telemetry, analytics, cloud tracking, or remote licensing beacons. UniversalDocsGrabber complies with runtime invariant `INV-LOCAL-01`.
3. **RunAsInvoker Unprivileged Execution (INV-SEC-02)**: The application requires zero elevated privileges (`RunAsInvoker`), writing only to `%USERPROFILE%\.univ_docs_grabber\` and user-selected download directories.
4. **Static Web/PWA Companion Zero-Dependency Boundary (INV-PWA-07)**: The web/PWA companion (`web_companion/`) contains **0 external npm dependencies**, running entirely on native browser APIs, Service Workers, and pure JavaScript.

---

## 2. Direct Runtime Python Dependencies

All packages below are specified in [`requirements.txt`](requirements.txt) and verified against PyPI upstream records:

| Package | Specification | Upstream License | Usage & Architectural Role | Egress / Privilege Profile |
|---|---|---|---|---|
| **PySide6** | `>=6.5` | LGPL-3.0-only / GPL-2.0-only / GPL-3.0-only | Official Qt for Python GUI bindings (Widgets, Event Loop, System Tray, File Dialogs) | 100% Offline, unprivileged GUI execution, dynamically linked |
| **pypdf** | `>=3.15` | BSD-3-Clause | Pure-Python PDF extraction, page merging, metadata inspection | 100% Offline in-memory parsing, zero network socket calls |
| **reportlab** | `>=4.0` | BSD License | PDF generation engine for converting plain-text email bodies to PDF | Local PDF drawing engine, zero telemetry |
| **Pillow** | `>=10.0` | HPND / MIT-CMU | Image loading, processing, and multi-image PDF assembly | Local image rasterization, zero network activity |
| **xhtml2pdf** | `>=0.2.11` | Apache-2.0 | HTML to PDF rendering for rich HTML email messages | Local HTML-to-PDF compiler, no external asset downloading |
| **keyring** | `>=24.0` | MIT | Secure credential vault interface (Windows Credential Vault) | Native OS credential store API, no network calls |
| **pytesseract** | `>=0.3.10` | Apache-2.0 | Python wrapper for local Tesseract-OCR CLI binary | Local subprocessing (`subprocess.run`), zero egress |
| **pdf2image** | `>=1.17.0` | MIT | Converts PDF pages to Pillow images for OCR preprocessing | Local Poppler wrapper, zero network activity |
| **pywin32** | `>=306` (Windows) | PSF License | Windows COM automation (`win32com.client`) for Word-to-PDF conversion | Local Windows API / Word OLE automation |
| **docx2pdf** | `>=0.1.8` | MIT | Secondary Word/DOCX to PDF conversion fallback | Local Word automation wrapper |

---

## 3. Transitive Qt for Python Wheels

Installed automatically via the official `PySide6` wheel distribution:

| Package | Specification | License | Dynamic Linking Transparency & Compliance Notice |
|---|---|---|---|
| **PySide6_Essentials** | Transitive | LGPL-3.0-only / GPL-2.0 / GPL-3.0 | Contains QtCore, QtGui, QtWidgets. Dynamically linked; users retain full freedom to replace Qt shared libraries per LGPLv3 §4. |
| **PySide6_Addons** | Transitive | LGPL-3.0-only / GPL-2.0 / GPL-3.0 | Optional Qt modules; dynamically loaded at runtime. |
| **shiboken6** | Transitive | LGPL-3.0-only / GPL-2.0 / GPL-3.0 | CPython/C++ binding generator runtime shared libraries. |

---

## 4. Static Web / PWA Companion

The companion in `web_companion/` provides offline document review on mobile and auxiliary devices:

| Component | Dependency Count | External Assets | Security & Data Boundary |
|---|---|---|---|
| **PWA Web App** | 0 external npm packages | 0 CDN scripts | Reads only redacted `docsgrabber-library-v1.json` via local drag-and-drop or file input. 100% client-side DOM rendering. |
| **Service Worker** | Native `sw.js` | 0 remote origins | Caches local icons, styles, and scripts for offline-first reliability. |

---

## 5. Development & Testing Toolchain

| Tool | Environment | License | Scope & Isolation |
|---|---|---|---|
| **pytest** | Development / CI | MIT | Test runner for contract, integration, and platform smoke suites |
| **ruff** | Development / CI | MIT / Apache-2.0 | Extremely fast Python linter and formatter (configured in `pyproject.toml`) |
| **setuptools** | Build System | MIT | PEP 517 / PEP 621 build backend (`setuptools.build_meta`) |
| **Node.js Test Runner** | CI / Companion Tests | MIT | Native `node --test` runner for companion contract and PWA tests |

---

## 6. Optional System Prerequisites (External Binaries)

These tools are optional external system binaries managed by the operating system or user, not distributed by UniversalDocsGrabber:
- **Tesseract OCR**: Licensed under Apache License 2.0. Optional for scanning image-only PDFs.
- **Poppler**: Licensed under GPLv2/GPLv3. External CLI utility (`pdftoppm`) invoked via subprocess for PDF page rendering during OCR.
- **Microsoft Office / Word**: Commercial desktop software. Optional for Microsoft Word OLE automation conversion on Windows.

---

## 7. License Compatibility & Redistribution Guidelines

1. **Permissive MIT Base**: UniversalDocsGrabber's core application code is released under the permissive MIT license.
2. **LGPLv3 Compliance Assurance**: When bundling or distributing binary packages with PySide6:
   - Dynamic linking must be preserved (do not statically compile PySide6 into a single monolithic binary without providing relinking capability).
   - Upstream LGPL-3.0 license text and notices must be included.
   - End-users must remain free to swap Qt libraries with compatible ABI versions.
3. **Patent & Indemnity**: No proprietary patents or viral copyleft restrictions contaminate this repository.

*Document maintained under the doc-bricks open-source governance framework. Audit verified clean on 2026-09-22 (prior baseline 2026-09-14).*