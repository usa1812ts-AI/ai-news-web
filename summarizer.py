"""
Summarizer – fasst Newsletter-Inhalte mit OpenAI API zusammen.
Gibt eine deutsche Zusammenfassung in Stichpunkten zurück.
"""

import os
from openai import OpenAI


def summarize_newsletters(newsletters: list[dict]) -> str:
    """
    Fasst eine Liste von Newslettern auf Deutsch zusammen.

    Args:
        newsletters: Liste von Dicts mit 'subject', 'from', 'body'

    Returns:
        Formatierte Zusammenfassung als String für Telegram
    """
    if not newsletters:
        return "📭 Heute keine neuen AI-Newsletter gefunden."

    # Baue den Kontext aus allen Newslettern
    newsletter_texts = []
    for i, nl in enumerate(newsletters, 1):
        newsletter_texts.append(
            f"--- Newsletter {i}: {nl['subject']} (von: {nl['from']}) ---\n"
            f"{nl['body']}"
        )

    combined = "\n\n".join(newsletter_texts)

    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    prompt = f"""Du bist ein AI-News-Analyst. Fasse die folgenden AI-Newsletter 
zusammen. Die Zusammenfassung ist für einen Sales Engineer im Maschinenbau, 
der sich für AI-Trends, Produktivität und Business-Anwendungen interessiert.

REGELN:
- Schreibe auf Deutsch
- Nutze Stichpunkte (•)
- Maximal 8-10 der wichtigsten Neuigkeiten
- Pro Stichpunkt: 1-2 Sätze, knapp und informativ
- Gruppiere nach Relevanz (wichtigstes zuerst)
- Ignoriere Werbung, Sponsoring und Affiliate-Links
- Wenn mehrere Newsletter dasselbe Thema behandeln, fasse es zusammen
- Ergänze am Ende einen kurzen "🎯 Praxis-Tipp" – eine konkrete Handlungsempfehlung

NEWSLETTER-INHALTE:
{combined}

Antworte NUR mit der formatierten Zusammenfassung. Kein Smalltalk."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    summary = response.choices[0].message.content

    # Formatiere für Telegram – Datum und Uhrzeit MEZ/MESZ des Durchlaufs
    from datetime import datetime
    from zoneinfo import ZoneInfo
    now_mez = datetime.now(ZoneInfo("Europe/Berlin"))
    timestamp = now_mez.strftime("%d.%m.%Y um %H:%M Uhr MEZ")
    header = f"🤖 *AI News Briefing*\n📅 {timestamp}\n{'─' * 30}\n\n"

    return header + summary


if __name__ == "__main__":
    # Test mit Dummy-Daten
    from dotenv import load_dotenv
    load_dotenv()

    test_newsletters = [
        {
            "subject": "Test Newsletter",
            "from": "Test Sender",
            "date": "2026-04-10",
            "body": "OpenAI hat GPT-5 angekündigt. Google bringt Gemini 3.0. "
                    "Anthropic veröffentlicht Claude 4.6 mit neuen Features.",
        }
    ]

    result = summarize_newsletters(test_newsletters)
    print(result)
