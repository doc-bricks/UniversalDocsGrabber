# Beitragsrichtlinie / Contributing Guide

## Deutsch

Vielen Dank für Ihr Interesse, zu diesem Projekt beizutragen.

### Wie Sie beitragen können

1. **Bug melden:** Erstellen Sie ein Issue mit dem Label `bug`
2. **Feature vorschlagen:** Erstellen Sie ein Issue mit dem Label `enhancement`
3. **Code beitragen:** Erstellen Sie einen Pull Request

### Pull Requests

1. Forken Sie das Repository
2. Erstellen Sie einen Feature-Branch: `git checkout -b feature/mein-feature`
3. Committen Sie Ihre Änderungen: `git commit --signoff -m "Beschreibung der Änderung"`
4. Pushen Sie den Branch: `git push origin feature/mein-feature`
5. Erstellen Sie einen Pull Request

### Developer Certificate of Origin (DCO)

Dieses Projekt verwendet den [Developer Certificate of Origin (DCO)](https://developercertificate.org/). Bitte signieren Sie jeden Commit mit `--signoff`:

```bash
git commit --signoff -m "Beschreibung der Änderung"
```

Damit bestätigen Sie, dass Sie das Recht haben, den Code unter der Projektlizenz einzureichen.

### Code-Richtlinien

- Python: PEP 8 Stil
- Encoding: UTF-8 für alle Dateien
- Sprache: Code und Kommentare auf Deutsch oder Englisch
- Keine hardcoded Pfade oder API-Keys
- Keine lokalen Konfigurationsdateien, Mail-Metadaten oder heruntergeladenen Dokumente committen

### Erste Schritte

```bash
git clone https://github.com/doc-bricks/UniversalDocsGrabber.git
cd UniversalDocsGrabber
pip install -r requirements.txt
python UniversalDocsGrabberV1.py
```

---

## English

Thank you for your interest in contributing to this project.

### How to Contribute

1. **Report bugs:** Create an issue with the `bug` label
2. **Suggest features:** Create an issue with the `enhancement` label
3. **Contribute code:** Create a pull request

### Pull Requests

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/my-feature`
3. Commit your changes: `git commit --signoff -m "Description of change"`
4. Push the branch: `git push origin feature/my-feature`
5. Create a pull request

### Developer Certificate of Origin (DCO)

This project uses the [Developer Certificate of Origin (DCO)](https://developercertificate.org/). Please sign off every commit with `--signoff`:

```bash
git commit --signoff -m "Description of change"
```

This certifies that you have the right to submit the code under the project license.

### Code Guidelines

- Python: PEP 8 style
- Encoding: UTF-8 for all files
- Language: code and comments in German or English
- No hardcoded paths or API keys
- Do not commit local configuration files, mail metadata, or downloaded documents

### Getting Started

```bash
git clone https://github.com/doc-bricks/UniversalDocsGrabber.git
cd UniversalDocsGrabber
pip install -r requirements.txt
python UniversalDocsGrabberV1.py
```
