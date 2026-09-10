# Privacy Policy — UniversalDocsGrabber

Last updated: September 10, 2026

UniversalDocsGrabber is designed around a **100% local-first, zero-telemetry** privacy model.

## 1. No Data Collection or Egress
- UniversalDocsGrabber does not collect, track, or transmit any personal data, analytics, crash reports, or telemetry to external servers.
- The application operates entirely offline on your local machine, with network communication strictly limited to the user-configured IMAP server over secure SSL/TLS.

## 2. Credentials and Passwords
- All email account credentials (usernames and passwords) are stored locally in the secure Windows Credential Vault (via Python `keyring`).
- No passwords or tokens are stored in plain text or written to configuration files.

## 3. Redacted Companion Export
- When creating export bundles (`docsgrabber-library-v1.json`) for the Web/PWA companion, all sensitive data is redacted.
- The export contains only document filenames, dates, categories, and account references (`account-<sha256>`). It strictly never contains credentials, email message bodies, or raw PDF/attachment contents.

## 4. Third-Party Services
- UniversalDocsGrabber does not use third-party analytics, advertisements, or tracking SDKs.

## 5. Contact
For questions regarding privacy or security, open an issue on the repository:
https://github.com/doc-bricks/UniversalDocsGrabber/issues
