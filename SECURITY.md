# Security Policy / Sicherheitsrichtlinie

[English](#english) | [Deutsch](#deutsch)

---

<a name="english"></a>
## English

### Supported Versions

We provide security updates and patches for the following versions of UniversalDocsGrabber:

| Version | Supported | Status |
|---------|-----------|--------|
| `1.1.x` | :white_check_mark: | Active Security Support |
| `1.0.x` | :white_check_mark: | Maintenance / Critical Fixes Only |
| `< 1.0.0` | :x: | End of Life (Upgrade Recommended) |

### Reporting a Vulnerability

If you discover a security vulnerability or potential data leak in UniversalDocsGrabber, please do NOT open a public issue on GitHub. We adhere to coordinated vulnerability disclosure:

1. **GitHub Private Vulnerability Reporting (Preferred):**
   Navigate to [Report a vulnerability](https://github.com/doc-bricks/UniversalDocsGrabber/security/advisories/new) in the GitHub repository to file a confidential report.
2. **Direct Contact:**
   Send an encrypted or confidential email to:
   - `security@doc-bricks.org`
   - `security@open-bricks.org`
   - `security@ellmos.ai`
   - `support@lukasgeiger.com`
   - `lukas@open-bricks.org`

Include as much information as possible:
- Detailed description and reproduction steps
- Sample file or Proof of Concept (PoC)
- Potential risk and impact assessment
- UniversalDocsGrabber version and operating system environment

### Response SLA & Timelines

- **Initial Response & Confirmation:** Within **48 hours**.
- **Severity & Impact Triage:** Within **5 business days**.
- **Remediation & Patch Release:** Coordinated patch published via GitHub release and private advisory disclosure within 14 to 30 days depending on severity.

### Security Architecture & Invariants

UniversalDocsGrabber is built on a strict Local-First & Zero-Egress security architecture:

1. **Credential Protection & Windows Vault (INV-CRED-03):**
   Mailbox credentials (IMAP passwords, app passwords, OAuth tokens) are never stored in plain text configuration files. All secrets are managed securely via the OS credential store (Windows Credential Vault / `keyring`).
2. **Zero-Telemetry & Local Processing (INV-LOCAL-01):**
   Zero telemetry, zero analytics, and zero external tracking are embedded in the application. All email parsing, attachment downloading, PDF conversion, and Tesseract OCR processing occur strictly on the user's local machine (Zero-Egress).
3. **Redacted Web/PWA Companion Isolation (INV-REDACT-04, INV-PWA-07):**
   The static Web/PWA companion (`web_companion/`) operates exclusively on redacted export datasets (`docsgrabber-library-v1.json`). Redacted exports strictly exclude mail passwords, IMAP credentials, full email bodies, raw document payloads, and authentication tokens. The PWA is 100% static, client-side only, and does not require or communicate with any cloud backend.
4. **Filesystem & Privilege Boundaries (INV-SEC-02):**
   UniversalDocsGrabber runs strictly in user space (Non-Elevation / `RunAsInvoker`) and requires no administrative elevation. Configuration and local metadata are confined to `%USERPROFILE%\.univ_docs_grabber\` and user-specified export directories.
5. **Non-Destructive Processing:**
   Original downloaded files and mail attachments are preserved without in-place destruction; OCR and format conversions produce distinct target files.

---

<a name="deutsch"></a>
## Deutsch

### Unterstützte Versionen

Sicherheitsupdates und Patches werden für folgende UniversalDocsGrabber-Versionen bereitgestellt:

| Version | Unterstützt | Status |
|---------|-------------|--------|
| `1.1.x` | :white_check_mark: | Aktiver Sicherheits-Support |
| `1.0.x` | :white_check_mark: | Wartungsmodus / Nur kritische Fehler |
| `< 1.0.0` | :x: | End of Life (Upgrade empfohlen) |

### Melden einer Schwachstelle

Wenn Sie eine Sicherheitslücke oder einen potenziellen Datenabfluss in UniversalDocsGrabber vermuten, eröffnen Sie bitte KEIN öffentliches Issue auf GitHub. Wir bitten um vertrauliche Koordinierung:

1. **GitHub Private Vulnerability Reporting (Bevorzugt):**
   Navigieren Sie im GitHub-Repository zu [Schwachstelle melden (Security Advisory)](https://github.com/doc-bricks/UniversalDocsGrabber/security/advisories/new) für einen vertraulichen Bericht.
2. **Direkter Kontakt:**
   Senden Sie eine E-Mail an:
   - `security@doc-bricks.org`
   - `security@open-bricks.org`
   - `security@ellmos.ai`
   - `support@lukasgeiger.com`
   - `lukas@open-bricks.org`

Bitte fügen Sie Ihrem Bericht folgende Details bei:
- Schritte zur Reproduktion der Schwachstelle
- Beispieldatei oder Proof-of-Concept (PoC)
- Potenzielle Auswirkungen und Risikobewertung
- UniversalDocsGrabber-Version und Betriebssystemumgebung

### Reaktionszeiten (SLA)

- **Erste Rückmeldung:** Innerhalb von **48 Stunden**.
- **Triage & Risikobewertung:** Innerhalb von **5 Werktagen**.
- **Bereitstellung eines Fixes:** Koordiniertes Release über GitHub-Advisory und neue Patch-Version innerhalb von 14 bis 30 Tagen.

### Sicherheits- und Datenschutz-Invarianten

1. **Zugangsdaten & Windows Tresor (INV-CRED-03):**
   Mailbox-Passwörter und IMAP-Zugangsdaten werden niemals im Klartext in Konfigurationsdateien gespeichert. Die Sicherung erfolgt über den Windows Credential Vault (`keyring`).
2. **Lokale Verarbeitung & Null-Telemetrie (INV-LOCAL-01):**
   Keine Telemetrie, keine externen Analysedienste oder Tracking-Bibliotheken (Zero-Egress). E-Mail-Filterung, Anhang-Download, PDF-Konvertierung und Tesseract-OCR laufen vollständig lokal auf dem Client.
3. **Redigierte Web/PWA-Companion-Isolation (INV-REDACT-04, INV-PWA-07):**
   Der statische Web/PWA-Companion (`web_companion/`) liest ausschließlich unbedenkliche, redigierte Bibliotheks-Exporte (`docsgrabber-library-v1.json`). Passwörter, IMAP-Verbindungsdaten, vollständige Mail-Texte und Dateiinhalte werden im Export standardmäßig eliminiert.
4. **Berechtigungsgrenzen (INV-SEC-02):**
   Die Anwendung erfordert keine Administrator-Rechte (Non-Elevation / `RunAsInvoker`). Konfiguration und Metadaten bleiben im Benutzerprofil (`%USERPROFILE%\.univ_docs_grabber\`).
5. **Verlustfreie Dateiverarbeitung (Non-Destructive):**
   Originalanhänge und Quelldokumente werden niemals destruktiv überschrieben; Konvertierungen und OCR-Ergebnisse werden als separate Zieldateien abgelegt.