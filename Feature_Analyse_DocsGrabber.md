# Feature-Analyse: DocsGrabber (Gmail + Universal)

## Kurzbeschreibung
Ein umfassendes Tool zum automatischen Download von Dokumenten aus E-Mails. Verfügbar in zwei Varianten: Gmail-spezifisch (Google API) und Universal (IMAP für alle Anbieter). Unterstützt OCR, PDF-Konvertierung und Such-Profile.

---

## ✨ Highlights

| Feature | Beschreibung |
|---------|-------------|
| **Gmail API** | Native Google API Integration |
| **Universal IMAP** | Funktioniert mit allen E-Mail-Anbietern |
| **Such-Profile** | Speicherbare Suchkriterien mit Zielordnern |
| **OCR-Integration** | Tesseract für Texterkennung in Bildern |
| **PDF-Konvertierung** | HTML→PDF, DOCX→PDF, Bilder→PDF |
| **Hash-Check** | Duplikat-Erkennung via SHA256 |
| **Multi-Format** | PDF, DOCX, DOC, JPG, PNG |
| **Dokumenten-DB** | JSON-basierte Verwaltung |

---

## 📊 Feature-Vergleich

| Feature | DocsGrabber | Thunderbird | Mail Export | manuell |
|---------|:-----------:|:-----------:|:-----------:|:-------:|
| Auto-Download | ✅ | ❌ | ⚠️ | ❌ |
| Such-Profile | ✅ | ⚠️ | ❌ | ❌ |
| OCR | ✅ | ❌ | ❌ | ❌ |
| PDF-Konvert | ✅ | ❌ | ⚠️ | ❌ |
| Multi-Provider | ✅ | ✅ | ⚠️ | ✅ |
| Hash-Duplikate | ✅ | ❌ | ❌ | ❌ |

---

## 🎯 Bewertung

### Aktueller Stand: **Production Ready (85%)**

| Kategorie | Bewertung |
|-----------|:---------:|
| Funktionsumfang | ⭐⭐⭐⭐⭐ |
| UI/UX | ⭐⭐⭐⭐ |
| Stabilität | ⭐⭐⭐⭐ |

**Gesamtbewertung: 8.5/10** - Professionelles Dokument-Management

---

## 🚀 Empfohlene Erweiterungen

1. **Scheduler** - Automatischer periodischer Scan
2. **Cloud-Sync** - Upload zu OneDrive/Dropbox
3. **Kategorisierung** - Auto-Sortierung nach Typ
4. **Outlook-Support** - Microsoft Graph API

---

## 💻 Technische Details

```
Framework:      PyQt6
Gmail:          Google API (gmail.readonly)
Universal:      IMAP + keyring
OCR:            pytesseract, pdf2image
PDF:            xhtml2pdf, reportlab, pypdf
Konvertierung:  win32com, docx2pdf
```

### Varianten:
- **GmailDocsGrabberV5**: 853 Zeilen (Gmail-spezifisch)
- **UniversalDocsGrabberV1**: 746 Zeilen (IMAP universal)

---
*Analyse erstellt: 02.01.2026*
