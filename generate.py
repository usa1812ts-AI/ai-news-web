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

load_dotenv()

from gmail_reader import read_todays_newsletters
from summarizer import summarize_newsletters


def main():
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
    if "─" in summary_text:
        separator_idx = summary_text.index("─")
        # Find end of separator line
        end_idx = summary_text.index("\n", separator_idx)
        summary_text = summary_text[end_idx:].strip()

    # Schritt 3: JSON schreiben
    print("\n💾 Schritt 3: JSON schreiben...")
    now_mez = datetime.now(ZoneInfo("Europe/Berlin"))

    data = {
        "generated_at": now_mez.isoformat(),
        "sources": sources,
        "summary": summary_text,
        "newsletter_count": len(newsletters) if newsletters else 0,
    }

    os.makedirs("docs/data", exist_ok=True)
    with open("docs/data/latest.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("   ✅ docs/data/latest.json geschrieben")
    print("\n" + "=" * 50)
    print("✅ AI News Web Generator abgeschlossen!")


if __name__ == "__main__":
    main()
