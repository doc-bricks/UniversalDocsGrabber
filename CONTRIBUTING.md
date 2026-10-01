# Contributing to UniversalDocsGrabber / Mitwirken an UniversalDocsGrabber

Welcome! We welcome contributions to `UniversalDocsGrabber` (Local-first email attachment downloader, OCR processor, and document organizer). To maintain air-gapped process isolation, credential security, single-writer filesystem integrity, and compliance across multi-host environments, all contributions must adhere to the quality standards and operational invariants defined below.

---

## English

### 1. General Principles & Quality Gates
1. **Local-First & Zero-Egress (`INV-LOCAL-01`)**: All document ingestion, parsing, OCR, and categorization execute strictly on localhost without outbound cloud telemetry, analytics, or unsolicited network sockets.
2. **Unprivileged User-Mode Execution (`INV-SEC-02` / `RunAsInvoker`)**: All background fetchers, CLI invocations, and GUI workflows execute strictly in unprivileged user space without administrative elevation or root permissions.
3. **OS Keyring Vaulting (`INV-CRED-03`)**: Mailbox credentials must never be written to disk in plaintext; they are securely vaulted via `keyring` in the Windows Credential Vault.
4. **Sanitized Export Schema (`INV-REDACT-04`)**: Companion exports (`docsgrabber-library-v1.json`) must never contain passwords, tokens, or raw email bodies.
5. **SHA-256 Deduplication (`INV-HASH-05`)**: Content hash verification prevents duplicate downloads and redundant disk writes.
6. **Graceful Degradation (`INV-FALL-06`)**: Soft fallbacks ensure the tool continues operating reliably even when external tools (Word, Poppler, Tesseract OCR) are unavailable.
7. **Zero-Dependency Static PWA (`INV-PWA-07`)**: The `web_companion/` companion operates strictly offline with zero external npm or CDN dependencies.
8. **100% Permissive Open Source (`INV-LIC-08`)**: UniversalDocsGrabber is released under the MIT License; all direct runtime dependencies are permissive, and PySide6 is dynamically linked under LGPLv3. Zero copyleft contamination.
9. **48h Security & Governance SLA (`INV-SLA-09`)**: Maintain 48h acknowledgement and 5-business-day triage commitments for security reports per `SECURITY.md`.
10. **Bilingual Contract Parity (`INV-PAR-10`)**: Maintain synchronized structural and navigational parity across `README.md` and `README-DE.md` (18-point dual anchors `sec-01` through `sec-18`).
11. **Version Freeze Discipline (`T-20260920-167562623`)**: Version `1.1.7` is strictly frozen across all manifests. Do not bump the version string. Document all advancements under `## [Unreleased]` in `CHANGELOG.md`.
12. **Clean Code & Regression Testing**: Every feature or fix must include regression tests in `tests/`. Keep test coverage at 100% pass rate.

### 2. Local Development Workflow (Plan D)
```bash
# Clone and enter the canonical Plan D repository
cd "C:\_Local_DEV\repos\UniversalDocsGrabber"

# Install package with development dependencies
python -m pip install -e ".[dev]"

# Run comprehensive test suite
PYTHONIOENCODING=utf-8 python -m pytest -ra -v

# Run linter
python -m ruff check .

# Check bytecode compilation
python -m compileall -q .

# Check whitespace and git diff cleanliness
git diff --check

# Verify version freeze discipline (0 version modifications)
git diff -G"version = "
```

### 3. Submission Protocol
- Sign all commits (`git commit --signoff`) confirming the Developer Certificate of Origin (DCO).
- Never commit credentials, tokens, `.env` files, or local user mailbox caches.
- Ensure all 10 governance invariants (`INV-LOCAL-01` to `INV-PAR-10`) remain VERIFIED.

---

## Deutsch

### 1. Grundsätze & Qualitäts-Tore
1. **Local-First & Zero-Egress (`INV-LOCAL-01`)**: Sämtliche Download-, Parsing-, OCR- und Ablage-Abläufe arbeiten standardmäßig zu 100% offline auf dem lokalen Rechner ohne Telemetrie, Sockets oder externe Datenübertragung.
2. **Unprivilegierte Benutzer-Ausführung (`INV-SEC-02` / `RunAsInvoker`)**: Sämtliche Hintergrund-Fetcher, CLI-Aufrufe und GUI-Prozesse laufen strikt im unprivilegierten Standard-Benutzerkontext ohne administrative Rechte oder UAC-Elevation.
3. **Betriebssystem-Schlüsseltresor (`INV-CRED-03`)**: Mailbox-Passwörter werden niemals im Klartext gespeichert, sondern sicher im Windows Credential Vault via `keyring` hinterlegt.
4. **Bereinigtes Exportschema (`INV-REDACT-04`)**: Exportdateien (`docsgrabber-library-v1.json`) für den Web/PWA-Begleiter enthalten zu keinem Zeitpunkt Passwörter, Token oder vollständige E-Mail-Texte.
5. **Kryptografische SHA-256 Deduplizierung (`INV-HASH-05`)**: Inhalts-Prüfsummen verhindern redundante Downloads und doppelte Dateispeicherung.
6. **Sanfte Fehlerdegradation (`INV-FALL-06`)**: Fehlende Drittwerkzeuge (Microsoft Word, Poppler, Tesseract OCR) führen zu verständlichen Warnungen statt zu Systemabstürzen.
7. **Autarker Web/PWA-Begleiter (`INV-PWA-07`)**: Die Web-Begleitanwendung (`web_companion/`) kommt ohne externe npm-Pakete oder CDNs aus und ist vollständig offline-fähig.
8. **100% Zulässiger Open-Source-Stack (`INV-LIC-08`)**: UniversalDocsGrabber steht unter der MIT-Lizenz. Alle Abhängigkeiten sind permissiv lizenziert; PySide6 ist dynamisch nach LGPLv3 eingebunden. Reiner Zero-Copyleft Schutz.
9. **48h Sicherheits- & Governance-SLA (`INV-SLA-09`)**: Verbindliche Erstbestätigung binnen 48 Stunden und Triage binnen 5 Werktagen gemäß `SECURITY.md`.
10. **Zweisprachige Vertragsparität (`INV-PAR-10`)**: Synchrone 18-Punkte-Navigationsparität mit dualen HTML-Ankern (`sec-01` bis `sec-18`) über `README.md` und `README-DE.md`.
11. **Strikte Versions-Freeze-Disziplin (`T-20260920-167562623`)**: Version `1.1.7` bleibt in allen Manifesten eingefroren. Keine Versionserhöhung vornehmen; alle Änderungen unter `## [Unreleased]` in `CHANGELOG.md` festhalten.
12. **Testabdeckung & Regressionstests**: Für jede Verhaltensänderung ist ein Vertragstest in `tests/` zu ergänzen. Die Testsuite muss zu 100% grün bleiben.

### 2. Lokaler Entwicklungsablauf (Plan D)
```bash
# Kanonischen Plan D Klon ansteuern
cd "C:\_Local_DEV\repos\UniversalDocsGrabber"

# Entwicklungsumgebung einrichten
python -m pip install -e ".[dev]"

# Vollständige Testsuite ausführen
PYTHONIOENCODING=utf-8 python -m pytest -ra -v

# Linter-Prüfung
python -m ruff check .

# Bytecode-Kompilierung
python -m compileall -q .

# Diff- und Whitespace-Prüfung
git diff --check

# Versions-Freeze prüfen (0 Versions-Modifikationen)
git diff -G"version = "
```

### 3. Einreichung
- Commits per DCO signieren (`git commit --signoff`).
- Keine Zugangsdaten, Passwörter oder persönliche Mail-Daten committen.
- Alle 10 Invarianten (`INV-LOCAL-01` bis `INV-PAR-10`) müssen erfüllt bleiben.
