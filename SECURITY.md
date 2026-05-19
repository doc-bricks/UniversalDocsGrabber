# Security Policy

## Reporting a Vulnerability

If you find a security vulnerability, please report it responsibly:

1. **Do not open a public issue**
2. **Use GitHub's private vulnerability reporting:** Repository -> Security -> Advisories -> New
3. Include a description, steps to reproduce, affected versions, and potential impact

## Scope

- IMAP account configuration and mailbox access
- Local document downloads and conversion output
- Local metadata files below `%USERPROFILE%\.univ_docs_grabber\`
- Optional OCR and PDF conversion integrations

Out of scope: public test fixtures that contain no real credentials, issues caused by unsupported third-party OCR or PDF tools, and vulnerabilities that require malicious local administrator access.

## Response

As a solo project, response times may vary. Critical issues will be prioritized. Please allow reasonable time before public disclosure.
