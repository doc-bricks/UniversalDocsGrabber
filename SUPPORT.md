# Support & Troubleshooting — UniversalDocsGrabber

## Getting Help
If you encounter any issues or have questions regarding UniversalDocsGrabber:
- **Issue Tracker:** https://github.com/doc-bricks/UniversalDocsGrabber/issues
- **Repository Documentation:** [README.md](README.md) and [README-DE.md](README-DE.md)
- **Security Policy:** [SECURITY.md](SECURITY.md)

## Common Troubleshooting Topics
1. **IMAP Authentication Failures:**
   - Ensure you are using an app-specific password if your mail provider requires two-factor authentication (e.g. Gmail App-Passwörter).
   - Verify that IMAP access is enabled in your email provider's settings.
2. **Missing OCR Text Layer:**
   - OCR features rely on locally installed Tesseract-OCR and Poppler binaries.
   - If Tesseract/Poppler are not installed, UniversalDocsGrabber continues to download and convert files gracefully, logging an informational notice.
3. **Office / Word Conversion:**
   - On Windows, `.docx` and `.doc` conversion uses local Word COM automation or the `docx2pdf` utility.
   - If Microsoft Word is not installed, Word documents are saved directly in their original format.
