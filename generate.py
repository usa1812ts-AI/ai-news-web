"""
AI News Web Generator
Liest Gmail-Newsletter, erstellt Zusammenfassung,
schreibt Ergebnis nach docs/data/latest.json.
"""
import json
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

from gmail_reader import read_todays_newsletters
from summarizer import summarize_newsletters


def main():
    load_dotenv()

    print("🚀 AI News Web Generator gestartet...")
    print("=" * 50)

    # Schritt 1: Newsletter lesen
    print("\n📧 Schritt 1: Newsletter lesen...")
    try:
        newsletters = read_todays_newsletters()
    except Exception as e:
        print(f"❌ Gmail-Fehler: {e}")
        sys.exit(1)

    if not newsletters:
        summary_text = "📭 Heute keine neuen AI-Newsletter eingegangen."
        sources = []
        print("📭 Keine Newsletter heute.")
    else:
        print(f"   ✅ {len(newsletters)} Newsletter gefunden")
        sources = list({nl["from"] for nl in newsletters})

        # Schritt 2: Zusammenfassung erstellen
        print("\n🤖 Schritt 2: Zusammenfassung erstellen...")
        try:
            summary_text = summarize_newsletters(newsletters)
            print(f"   ✅ Zusammenfassung erstellt ({len(summary_text)} Zeichen)")
        except Exception as e:
            print(f"❌ Zusammenfassung fehlgeschlagen: {e}")
            sys.exit(1)

        # Telegram-Header entfernen (endet mit ─-Linie)
        TELEGRAM_SEPARATOR = "─" * 30
        if TELEGRAM_SEPARATOR in summary_text:
            after_sep = summary_text.index(TELEGRAM_SEPARATOR) + len(TELEGRAM_SEPARATOR)
            summary_text = summary_text[after_sep:].strip()
            print("   ✅ Telegram-Header entfernt")

    # Schritt 3: JSON schreiben
    print("\n💾 Schritt 3: JSON schreiben...")
    now_mez = datetime.now(ZoneInfo("Europe/Berlin"))

    data = {
        "generated_at": now_mez.isoformat(),
        "sources": sources,
        "summary": summary_text,
        "newsletter_count": len(newsletters),
    }

    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/latest.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("   ✅ docs/data/latest.json geschrieben")

    # Schritt 4: Archiv aktualisieren (letzte 7 Einträge)
    print("\n📚 Schritt 4: Archiv aktualisieren...")
    archive_path = "docs/data/archive.json"
    archive_entry = {
        "date": now_mez.strftime("%Y-%m-%d"),
        "generated_at": now_mez.isoformat(),
        "summary": summary_text,
    }

    if os.path.exists(archive_path):
        with open(archive_path, "r", encoding="utf-8") as f:
            archive = json.load(f)
    else:
        archive = []

    # Alten Eintrag desselben Tages entfernen (verhindert Duplikate bei Re-Run)
    today_str = now_mez.strftime("%Y-%m-%d")
    archive = [e for e in archive if e.get("date") != today_str]

    archive.insert(0, archive_entry)
    archive = archive[:7]

    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(archive, f, ensure_ascii=False, indent=2)
    print(f"   ✅ docs/data/archive.json aktualisiert ({len(archive)} Einträge)")

    print("\n" + "=" * 50)
    print("✅ AI News Web Generator abgeschlossen!")


if __name__ == "__main__":
    main()
