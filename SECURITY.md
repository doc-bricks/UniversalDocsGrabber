# Security Policy / Sicherheitsrichtlinie

## Reporting a Vulnerability / Sicherheitslücke melden

If you discover a security vulnerability or potential data leak in UniversalDocsGrabber, please report it responsibly:

1. **Do not open a public issue** on GitHub.
2. **Use GitHub's private vulnerability reporting:** `Repository -> Security -> Advisories -> New advisory`.
3. **Alternative direct security contact:** Send an encrypted or confidential email to `security@ellmos.ai` or `lukas@ellmos.ai`.
4. Include a detailed description, reproduction steps, affected versions, and potential risk assessment.

All security advisories are evaluated promptly. Please allow reasonable time for remediation before any public disclosure.

---

## Security Architecture & Invariants (English)

UniversalDocsGrabber is built on a strict **Local-First & Zero-Egress** security model designed for handling sensitive email attachments and documents:

1. **Credential Protection & Windows Vault**:
   - Mailbox credentials (IMAP passwords and OAuth tokens) are never stored in plain text configuration files.
   - Account secrets are managed securely via the OS credential store (Windows Credential Vault / `keyring`).
2. **Zero-Telemetry & Local Processing**:
   - Zero telemetry, zero analytics, and zero external tracking are embedded in the application.
   - All email parsing, attachment downloading, PDF conversion, and Tesseract OCR processing occur strictly on the user's local machine.
3. **Redacted Web/PWA Companion Isolation**:
   - The static Web/PWA companion (`web_companion/`) operates exclusively on redacted export datasets (`docsgrabber-library-v1.json`).
   - Redacted exports strictly exclude mail passwords, IMAP credentials, full email bodies, raw document payloads, and authentication tokens.
   - The PWA is 100% static, client-side only, and does not require or communicate with any cloud backend.
4. **Filesystem & Privilege Boundaries**:
   - UniversalDocsGrabber runs strictly in user space and requires no administrative elevation.
   - Configuration and local metadata are confined to `%USERPROFILE%\.univ_docs_grabber\` and user-specified export directories.

---

## Sicherheitsarchitektur & Invarianten (Deutsch)

UniversalDocsGrabber basiert auf einem strikten **Local-First & Zero-Egress** Sicherheitsmodell:

1. **Zugangsdaten & Windows Tresor**:
   - Mailbox-Passwörter und IMAP-Zugangsdaten werden niemals im Klartext in Konfigurationsdateien gespeichert.
   - Die Sicherung erfolgt über den Windows Credential Vault (`keyring`).
2. **Lokale Verarbeitung & Null-Telemetrie**:
   - Keine Telemetrie, keine externen Analysedienste oder Tracking-Bibliotheken.
   - E-Mail-Filterung, Anhang-Download, PDF-Konvertierung und Tesseract-OCR laufen vollständig lokal auf dem Client.
3. **Redacted Web/PWA Companion Isolation**:
   - Der statische Web/PWA-Companion (`web_companion/`) liest ausschließlich unbedenkliche, redigierte Bibliotheks-Exporte (`docsgrabber-library-v1.json`).
   - Passwörter, IMAP-Verbindungsdaten, vollständige Mail-Texte und Dateiinhalte werden im Export standardmäßig eliminiert.
4. **Berechtigungsgrenzen**:
   - Die Anwendung erfordert keine Administrator-Rechte (Non-Elevation).
