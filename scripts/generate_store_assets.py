#!/usr/bin/env python3
"""
generate_store_assets.py - Erzeugt Multi-Resolution Windows Store Tile-Assets,
Icons und Screenshots für UniversalDocsGrabber.
"""

from pathlib import Path
from PIL import Image, ImageDraw

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def generate_icons():
    """Erzeugt alle Store-Icon- und Tile-Größen aus dem Master-Icon."""
    icon_source = PROJECT_ROOT / "UniversalDocsGrabber_icon.png"
    if not icon_source.exists():
        icon_source = PROJECT_ROOT / "README" / "assets" / "icon.png"

    with Image.open(icon_source) as base_img:
        base = base_img.convert("RGBA")

        # Zielverzeichnisse
        target_dirs = [
            PROJECT_ROOT / "store_package" / "UniversalDocsGrabber" / "icons",
            PROJECT_ROOT / "store_package" / "UniversalDocsGrabber" / "assets",
            PROJECT_ROOT / "store_assets",
            PROJECT_ROOT / "assets" / "icons",
            PROJECT_ROOT / "releases" / "windowsstore",
        ]
        for d in target_dirs:
            d.mkdir(parents=True, exist_ok=True)

        # Standard Tile-Größen
        sizes = {
            "icon_44x44.png": (44, 44),
            "icon_50x50.png": (50, 50),
            "icon_150x150.png": (150, 150),
            "icon_310x310.png": (310, 310),
        }

        for name, size in sizes.items():
            resized = base.resize(size, Image.Resampling.LANCZOS)
            for d in [
                PROJECT_ROOT / "store_package" / "UniversalDocsGrabber" / "icons",
                PROJECT_ROOT / "store_package" / "UniversalDocsGrabber" / "assets",
                PROJECT_ROOT / "store_assets",
                PROJECT_ROOT / "assets" / "icons",
            ]:
                resized.save(d / name, format="PNG")

        # 310x150 Wide Tile (Zentriertes Icon auf 310x150 Canvas)
        wide = Image.new("RGBA", (310, 150), (0, 0, 0, 0))
        icon_fit = base.resize((130, 130), Image.Resampling.LANCZOS)
        offset_x = (310 - 130) // 2
        offset_y = (150 - 130) // 2
        wide.paste(icon_fit, (offset_x, offset_y), icon_fit)

        for d in [
            PROJECT_ROOT / "store_package" / "UniversalDocsGrabber" / "icons",
            PROJECT_ROOT / "store_package" / "UniversalDocsGrabber" / "assets",
            PROJECT_ROOT / "store_assets",
            PROJECT_ROOT / "assets" / "icons",
        ]:
            wide.save(d / "icon_310x150.png", format="PNG")

        # Aliase / kanonische Windows-SDK-Namen
        aliases = {
            "Square44x44Logo.png": "icon_44x44.png",
            "Square50x50Logo.png": "icon_50x50.png",
            "StoreLogo.png": "icon_50x50.png",
            "Square150x150Logo.png": "icon_150x150.png",
            "Wide310x150Logo.png": "icon_310x150.png",
            "Square310x310Logo.png": "icon_310x310.png",
        }
        for alias_name, src_name in aliases.items():
            for d in [
                PROJECT_ROOT / "store_package" / "UniversalDocsGrabber" / "icons",
                PROJECT_ROOT / "store_package" / "UniversalDocsGrabber" / "assets",
                PROJECT_ROOT / "store_assets",
            ]:
                src_file = d / src_name
                alias_file = d / alias_name
                with Image.open(src_file) as im:
                    im.save(alias_file, format="PNG")

        # StoreLogo.png in releases/windowsstore/
        store_logo_50 = base.resize((50, 50), Image.Resampling.LANCZOS)
        store_logo_50.save(PROJECT_ROOT / "releases" / "windowsstore" / "StoreLogo.png", format="PNG")

        print("[+] Alle Store Tile-Icons und Logos erfolgreich generiert.")


def generate_store_screenshots():
    """Erzeugt 4 hochauflösende 1920x1080 Store-Screenshots aus dem UI-Screenshot."""
    main_shot_path = PROJECT_ROOT / "README" / "screenshots" / "main.png"
    if not main_shot_path.exists():
        main_shot_path = PROJECT_ROOT / "screenshots" / "main.png"

    with Image.open(main_shot_path) as base_ui_img:
        ui_raw = base_ui_img.convert("RGBA")

        # 1920x1080 Canvas-Konfiguration
        canvas_w, canvas_h = 1920, 1080

        # Farbpalette (Dunkles Theme passend zu UniversalDocsGrabber: Marine/Slate/Blau)
        bg_color = (20, 26, 38, 255)
        card_bg = (30, 38, 54, 255)
        border_color = (55, 70, 96, 255)

        # Screenshot-Varianten mit echten Umlauten
        shots = [
            {
                "filename": "shot-1-inbox-and-rules.png",
                "title": "UniversalDocsGrabber — Lokaler E-Mail-Dokumentensauger",
                "subtitle": "Automatisierte Erfassung von Dokumenten und Anhängen direkt auf Ihrem PC",
                "tag": "POSTFACH & FILTER",
                "tag_color": (41, 128, 185, 255),
            },
            {
                "filename": "shot-2-document-extraction.png",
                "title": "Strukturierte Extraktion & automatische Ablage",
                "subtitle": "Kategorisierung nach Rechnungen, Verträgen und Nachweisen mit SHA-256 Deduplizierung",
                "tag": "EXTRAKTION & ARCHIV",
                "tag_color": (39, 174, 96, 255),
            },
            {
                "filename": "shot-3-ocr-and-conversion.png",
                "title": "OCR-Texterkennung & PDF-/Office-Konvertierung",
                "subtitle": "Volltextsuche in Scans via Tesseract sowie Word- und Dokumentenkonvertierung",
                "tag": "OCR & KONVERTIERUNG",
                "tag_color": (142, 68, 173, 255),
            },
            {
                "filename": "shot-4-companion-export.png",
                "title": "Redigierter Companion-Export & Datenschutz",
                "subtitle": "Sicherer Export für den mobilen Web/PWA-Companion ohne Weitergabe von Zugangsdaten",
                "tag": "COMPANION & DATENSCHUTZ",
                "tag_color": (211, 84, 0, 255),
            },
        ]

        target_dirs = [
            PROJECT_ROOT / "screenshots" / "store",
            PROJECT_ROOT / "README" / "screenshots" / "store",
            PROJECT_ROOT / "releases" / "windowsstore" / "screenshots",
        ]
        for td in target_dirs:
            td.mkdir(parents=True, exist_ok=True)

        for spec in shots:
            img = Image.new("RGBA", (canvas_w, canvas_h), bg_color)
            draw = ImageDraw.Draw(img)

            # Header-Leiste
            header_h = 110
            draw.rectangle([(0, 0), (canvas_w, header_h)], fill=(14, 18, 28, 255))
            draw.line([(0, header_h), (canvas_w, header_h)], fill=border_color, width=2)

            # Badge-Pill
            badge_x, badge_y = 60, 24
            badge_w, badge_h = 250, 28
            draw.rounded_rectangle(
                [(badge_x, badge_y), (badge_x + badge_w, badge_y + badge_h)],
                radius=6,
                fill=spec["tag_color"],
            )

            # Text auf Badge
            draw.text((badge_x + 16, badge_y + 6), spec["tag"], fill=(255, 255, 255, 255))

            # Titel & Untertitel
            draw.text((badge_x, badge_y + 36), spec["title"], fill=(240, 245, 252, 255))
            draw.text((badge_x, badge_y + 58), spec["subtitle"], fill=(160, 178, 205, 255))

            # UI Frame einpassen
            ui_w = 1760
            aspect = ui_raw.height / ui_raw.width
            ui_h = int(ui_w * aspect)
            if ui_h > 900:
                ui_h = 900
                ui_w = int(ui_h / aspect)

            ui_resized = ui_raw.resize((ui_w, ui_h), Image.Resampling.LANCZOS)

            pos_x = (canvas_w - ui_w) // 2
            pos_y = header_h + 25 + (920 - ui_h) // 2

            # Schatten / Rahmen um UI
            draw.rounded_rectangle(
                [(pos_x - 8, pos_y - 8), (pos_x + ui_w + 8, pos_y + ui_h + 8)],
                radius=10,
                fill=card_bg,
                outline=border_color,
                width=2,
            )

            # UI einfügen
            img.paste(ui_resized, (pos_x, pos_y), ui_resized if ui_resized.mode == "RGBA" else None)

            for td in target_dirs:
                img.save(td / spec["filename"], format="PNG")

        print("[+] Alle 4 Store-Screenshots (1920x1080) erfolgreich generiert.")


if __name__ == "__main__":
    generate_icons()
    generate_store_screenshots()
