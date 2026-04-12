"""
Gmail Reader – liest Newsletter-Mails mit dem Label 'RundownAgent'.
Extrahiert den Text-Inhalt und gibt ihn als Liste zurück.
"""

import os
import json
import base64
import re
from datetime import datetime, timedelta, timezone
from bs4 import BeautifulSoup
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]


def get_gmail_service():
    """Gmail API Service erstellen."""
    creds = None

    # Option 1: token.json als Datei (lokal)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # Option 2: Token aus Umgebungsvariable (GitHub Actions)
    elif os.environ.get("GMAIL_TOKEN_JSON"):
        token_data = json.loads(os.environ["GMAIL_TOKEN_JSON"])
        creds = Credentials.from_authorized_user_info(token_data, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            # Token aktualisieren wenn als Datei vorhanden
            if os.path.exists("token.json"):
                with open("token.json", "w") as f:
                    f.write(creds.to_json())
        else:
            raise RuntimeError(
                "Kein gültiges Gmail-Token. Führe zuerst auth_gmail.py aus."
            )

    return build("gmail", "v1", credentials=creds)


def extract_text_from_html(html_content: str) -> str:
    """HTML zu lesbarem Text konvertieren."""
    soup = BeautifulSoup(html_content, "html.parser")

    # Entferne Script/Style Tags
    for tag in soup(["script", "style", "head"]):
        tag.decompose()

    text = soup.get_text(separator="\n")

    # Bereinige: Mehrfache Leerzeilen entfernen
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)

    return text


def get_message_body(payload) -> str:
    """Extrahiert den Text aus einer Gmail-Nachricht (rekursiv für MIME)."""
    body_text = ""

    if payload.get("parts"):
        for part in payload["parts"]:
            mime_type = part.get("mimeType", "")

            if mime_type == "text/html":
                data = part.get("body", {}).get("data", "")
                if data:
                    html = base64.urlsafe_b64decode(data).decode("utf-8")
                    body_text = extract_text_from_html(html)
                    break
            elif mime_type == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    body_text = base64.urlsafe_b64decode(data).decode("utf-8")
            elif mime_type.startswith("multipart/"):
                body_text = get_message_body(part)
                if body_text:
                    break
    else:
        data = payload.get("body", {}).get("data", "")
        if data:
            decoded = base64.urlsafe_b64decode(data).decode("utf-8")
            mime_type = payload.get("mimeType", "")
            if mime_type == "text/html":
                body_text = extract_text_from_html(decoded)
            else:
                body_text = decoded

    return body_text


def read_todays_newsletters() -> list[dict]:
    """
    Liest alle Newsletter mit Label 'RundownAgent' der letzten 24 Stunden.

    Returns:
        Liste von Dicts mit 'subject', 'from', 'date', 'body'
    """
    service = get_gmail_service()

    # Suche: Label + letzte 24h
    yesterday = datetime.now(timezone.utc) - timedelta(hours=28)
    date_str = yesterday.strftime("%Y/%m/%d")
    query = f"label:RundownAgent after:{date_str}"

    print(f"📧 Suche Mails: {query}")

    results = service.users().messages().list(
        userId="me", q=query, maxResults=10
    ).execute()

    messages = results.get("messages", [])
    print(f"   → {len(messages)} Newsletter gefunden")

    newsletters = []
    for msg_meta in messages:
        msg = service.users().messages().get(
            userId="me", id=msg_meta["id"], format="full"
        ).execute()

        headers = {h["name"]: h["value"] for h in msg["payload"]["headers"]}

        body = get_message_body(msg["payload"])

        # Kürze auf ~4000 Zeichen um Token zu sparen
        if len(body) > 4000:
            body = body[:4000] + "\n\n[... gekürzt ...]"

        newsletters.append({
            "subject": headers.get("Subject", "Kein Betreff"),
            "from": headers.get("From", "Unbekannt"),
            "date": headers.get("Date", ""),
            "body": body,
        })

    return newsletters


if __name__ == "__main__":
    # Test
    from dotenv import load_dotenv
    load_dotenv()

    newsletters = read_todays_newsletters()
    for nl in newsletters:
        print(f"\n{'='*60}")
        print(f"📰 {nl['subject']}")
        print(f"📤 {nl['from']}")
        print(f"📅 {nl['date']}")
        print(f"📝 {nl['body'][:200]}...")
