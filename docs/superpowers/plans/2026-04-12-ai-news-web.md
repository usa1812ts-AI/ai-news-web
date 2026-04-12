# AI News Web App (PWA) — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Baut eine private PWA auf GitHub Pages, die täglich per GitHub Actions generierte KI-Newsletter-Zusammenfassungen anzeigt und manuellen Trigger via GitHub API unterstützt.

**Architecture:** GitHub Actions liest Gmail, ruft OpenAI API auf, schreibt Ergebnis als `docs/data/latest.json` ins Repo und pusht. GitHub Pages hostet die PWA aus dem `docs/`-Ordner. Die PWA (Vanilla JS) lädt die JSON-Datei, zeigt sie im T.S. Corporate Design an und kann via GitHub API einen neuen Lauf auslösen.

**Tech Stack:** Python 3.11, GitHub Actions, GitHub Pages, Vanilla JS, Web App Manifest, Service Worker, T.S. Corporate Design (Deep Olive `#2D362E`, Muted Orange `#D97706`)

---

## Datei-Übersicht

| Datei | Typ | Zweck |
|---|---|---|
| `gmail_reader.py` | Kopieren | Newsletter aus Gmail holen |
| `summarizer.py` | Kopieren | OpenAI Zusammenfassung |
| `generate.py` | Neu | Orchestrierung: liest + fasst zusammen + schreibt JSON |
| `requirements.txt` | Neu | Python-Abhängigkeiten |
| `.gitignore` | Neu | Schützt Secrets und Cache vor Git |
| `create_icons.py` | Neu | Einmaliges Erstellen der PWA-Icons (Pillow) |
| `docs/data/latest.json` | Neu | Initiale Platzhalterdaten |
| `docs/index.html` | Neu | PWA-Hauptseite (T.S. Design, alle 3 Screens) |
| `docs/app.js` | Neu | PIN-Logik, Daten laden, GitHub API Trigger |
| `docs/manifest.json` | Neu | PWA-Metadaten (installierbar auf iPhone/iPad) |
| `docs/service-worker.js` | Neu | Offline-Cache |
| `docs/icon-180.png` | Generiert | Apple Touch Icon (create_icons.py) |
| `docs/icon-192.png` | Generiert | PWA Icon |
| `docs/icon-512.png` | Generiert | PWA Icon groß |
| `.github/workflows/generate.yml` | Neu | Cron (18:00 MEZ) + manueller Trigger |

**Hinweis:** Die Web-Dateien liegen in `docs/` — das ist die GitHub-Pages-Quelle (einstellbar unter Repo-Settings → Pages → Source: `/docs`). Python-Dateien liegen im Root.

---

## Task 1: Python-Dateien kopieren + Projektfundament

**Files:**
- Kopieren: `gmail_reader.py` (aus ai-news-agent)
- Kopieren: `summarizer.py` (aus ai-news-agent)
- Erstellen: `requirements.txt`
- Erstellen: `.gitignore`

- [ ] **Schritt 1: Python-Dateien kopieren**

```bash
cp /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-agent/gmail_reader.py \
   /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web/gmail_reader.py

cp /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-agent/summarizer.py \
   /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web/summarizer.py
```

- [ ] **Schritt 2: requirements.txt erstellen**

Datei: `requirements.txt`

```
openai>=1.30.0
google-auth-oauthlib>=1.2.0
google-api-python-client>=2.150.0
python-dotenv>=1.0.1
requests>=2.32.0
beautifulsoup4>=4.12.0
Pillow>=10.0.0
```

- [ ] **Schritt 3: .gitignore erstellen**

Datei: `.gitignore`

```
# Python
__pycache__/
*.pyc
.env
venv/

# Gmail OAuth – NIEMALS ins Repo!
token.json
credentials.json

# macOS
.DS_Store

# Superpowers Brainstorming
.superpowers/
```

- [ ] **Schritt 4: Abhängigkeiten lokal installieren (Verifikation)**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
pip install -r requirements.txt
```

Erwartet: Alle Pakete installieren ohne Fehler.

- [ ] **Schritt 5: Commit**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
git add gmail_reader.py summarizer.py requirements.txt .gitignore
git commit -m "feat: project foundation — python files + gitignore"
```

---

## Task 2: generate.py — Orchestrierungs-Skript

**Files:**
- Erstellen: `generate.py`
- Erstellen: `docs/data/latest.json` (Platzhalter)

`generate.py` ist das neue Herzstück: Es ruft `gmail_reader` und `summarizer` auf und schreibt das Ergebnis als JSON in `docs/data/latest.json`.

- [ ] **Schritt 1: docs/data-Ordner und Platzhalter-JSON anlegen**

Ordner erstellen:
```bash
mkdir -p /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web/docs/data
```

Datei: `docs/data/latest.json`

```json
{
  "generated_at": "2026-04-12T18:00:00+02:00",
  "sources": [],
  "summary": "📭 Noch kein Briefing vorhanden.\n\nBitte 'Briefing neu generieren' drücken.",
  "newsletter_count": 0
}
```

- [ ] **Schritt 2: generate.py erstellen**

Datei: `generate.py`

```python
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
```

- [ ] **Schritt 3: Lokal testen (mit .env aus ai-news-agent)**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
cp ../ai-news-agent/.env .env
cp ../ai-news-agent/token.json .
python generate.py
```

Erwartet:
```
🚀 AI News Web Generator gestartet...
📧 Schritt 1: Newsletter lesen...
   ✅ X Newsletter gefunden
🤖 Schritt 2: Zusammenfassung erstellen...
   ✅ Zusammenfassung erstellt (XXX Zeichen)
💾 Schritt 3: JSON schreiben...
   ✅ docs/data/latest.json geschrieben
✅ AI News Web Generator abgeschlossen!
```

Dann prüfen ob `docs/data/latest.json` befüllt ist:
```bash
cat /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web/docs/data/latest.json
```
Erwartet: JSON mit `summary`-Feld, das eine echte Zusammenfassung enthält.

- [ ] **Schritt 4: .env und token.json aus Commit ausschließen (Verifikation)**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
git status
```

Erwartet: `.env` und `token.json` tauchen NICHT in der Liste auf (durch .gitignore geschützt).

- [ ] **Schritt 5: Commit**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
git add generate.py docs/data/latest.json
git commit -m "feat: generate.py orchestrator + initial latest.json"
```

---

## Task 3: GitHub Actions Workflow

**Files:**
- Erstellen: `.github/workflows/generate.yml`

Der Workflow ersetzt den manuellen Aufruf: Er läuft täglich um 18:00 MEZ und kann auch per App-Button ausgelöst werden.

**Wichtig:** `gmail_reader.py` liest den Gmail-Token direkt aus der Umgebungsvariable `GMAIL_TOKEN_JSON` — kein Dateischreiben nötig.

- [ ] **Schritt 1: Workflows-Ordner erstellen**

```bash
mkdir -p /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web/.github/workflows
```

- [ ] **Schritt 2: generate.yml erstellen**

Datei: `.github/workflows/generate.yml`

```yaml
name: AI News Briefing generieren

on:
  schedule:
    # 17:00 UTC = 18:00 MEZ (UTC+1) / 19:00 MESZ (UTC+2 im Sommer)
    # Im Sommer (MESZ) läuft es um 19:00 – das ist akzeptabel
    - cron: '0 17 * * *'
  workflow_dispatch:
    # Erlaubt manuellen Start via GitHub API und GitHub UI

permissions:
  contents: write  # Nötig um latest.json zu committen

jobs:
  generate:
    runs-on: ubuntu-latest

    steps:
      - name: Repository auschecken
        uses: actions/checkout@v4

      - name: Python 3.11 einrichten
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Abhängigkeiten installieren
        run: pip install -r requirements.txt

      - name: Briefing generieren
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          GMAIL_TOKEN_JSON: ${{ secrets.GMAIL_TOKEN_JSON }}
        run: python generate.py

      - name: Ergebnis committen und pushen
        run: |
          git config user.name "AI News Bot"
          git config user.email "actions@github.com"
          git add docs/data/latest.json
          git diff --staged --quiet || git commit -m "chore: briefing $(date -u +'%Y-%m-%d %H:%M UTC')"
          git push
```

- [ ] **Schritt 3: Commit**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
git add .github/workflows/generate.yml
git commit -m "feat: github actions workflow — cron + workflow_dispatch"
```

---

## Task 4: PWA-Icons generieren

**Files:**
- Erstellen: `create_icons.py` (einmalig lokal ausführen)
- Generiert: `docs/icon-180.png`, `docs/icon-192.png`, `docs/icon-512.png`

- [ ] **Schritt 1: create_icons.py erstellen**

Datei: `create_icons.py`

```python
"""
Erstellt die T.S.-Badge-Icons für die PWA.
Einmalig lokal ausführen: python create_icons.py
Benötigt Pillow (in requirements.txt enthalten).
"""
import os
from PIL import Image, ImageDraw, ImageFont


def create_badge(size: int) -> Image.Image:
    """Zeichnet den T.S.-Badge: Deep Olive Kreis + Orange Ring + weißer Text."""
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Deep Olive Hintergrundkreis
    draw.ellipse([0, 0, size - 1, size - 1], fill="#2D362E")

    # Muted Orange Ring (außen)
    ring = max(2, size // 30)
    draw.ellipse(
        [ring, ring, size - 1 - ring, size - 1 - ring],
        outline="#D97706",
        width=ring,
    )

    # T.S. Text (weiß, zentriert)
    font_size = size // 4
    font_path = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
    try:
        font = ImageFont.truetype(font_path, font_size)
    except OSError:
        # Fallback: Standard-Font (sieht schlechter aus, funktioniert aber)
        font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), "T.S.", font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    x = (size - tw) // 2 - bbox[0]
    y = (size - th) // 2 - bbox[1]
    draw.text((x, y), "T.S.", fill="#FFFFFF", font=font)

    return img


def main():
    os.makedirs("docs", exist_ok=True)
    for size in [180, 192, 512]:
        icon = create_badge(size)
        path = f"docs/icon-{size}.png"
        icon.save(path, "PNG")
        print(f"✅ {path} erstellt ({size}×{size}px)")
    print("Icons fertig!")


if __name__ == "__main__":
    main()
```

- [ ] **Schritt 2: Icons generieren**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
python create_icons.py
```

Erwartet:
```
✅ docs/icon-180.png erstellt (180×180px)
✅ docs/icon-192.png erstellt (192×192px)
✅ docs/icon-512.png erstellt (512×512px)
Icons fertig!
```

- [ ] **Schritt 3: Icons visuell prüfen**

```bash
open docs/icon-192.png
```

Erwartet: T.S.-Badge sichtbar — Deep Olive Kreis, orange Ring, weißes "T.S."

- [ ] **Schritt 4: Commit**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
git add create_icons.py docs/icon-180.png docs/icon-192.png docs/icon-512.png
git commit -m "feat: PWA icons — T.S. badge (180, 192, 512px)"
```

---

## Task 5: PWA-Metadaten (manifest.json + service-worker.js)

**Files:**
- Erstellen: `docs/manifest.json`
- Erstellen: `docs/service-worker.js`

- [ ] **Schritt 1: manifest.json erstellen**

Datei: `docs/manifest.json`

```json
{
  "name": "AI News Briefing",
  "short_name": "AI News",
  "description": "Tägliches KI-Newsletter-Briefing – T.S.",
  "start_url": "./",
  "display": "standalone",
  "background_color": "#2D362E",
  "theme_color": "#2D362E",
  "orientation": "portrait-primary",
  "icons": [
    {
      "src": "icon-192.png",
      "sizes": "192x192",
      "type": "image/png"
    },
    {
      "src": "icon-512.png",
      "sizes": "512x512",
      "type": "image/png",
      "purpose": "any maskable"
    }
  ]
}
```

- [ ] **Schritt 2: service-worker.js erstellen**

Datei: `docs/service-worker.js`

```javascript
const CACHE_NAME = 'ts-news-v1';

// Diese Dateien werden gecacht (funktionieren offline)
const CACHED_URLS = [
  './',
  './index.html',
  './app.js',
  './manifest.json',
  './icon-192.png',
];

// Installation: Dateien in Cache legen
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => cache.addAll(CACHED_URLS))
  );
  self.skipWaiting();
});

// Aktivierung: Alten Cache löschen
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== CACHE_NAME).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

// Fetch: latest.json immer frisch, Rest aus Cache
self.addEventListener('fetch', event => {
  if (event.request.url.includes('latest.json')) {
    // Daten immer frisch vom Server, Fallback auf Cache
    event.respondWith(
      fetch(event.request).catch(() => caches.match(event.request))
    );
    return;
  }

  // Alle anderen Ressourcen: Cache zuerst
  event.respondWith(
    caches.match(event.request).then(cached => cached || fetch(event.request))
  );
});
```

- [ ] **Schritt 3: Commit**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
git add docs/manifest.json docs/service-worker.js
git commit -m "feat: PWA manifest + service worker"
```

---

## Task 6: index.html — Hauptseite

**Files:**
- Erstellen: `docs/index.html`

Die Hauptseite enthält alle drei Screens (PIN, Hauptansicht, Ladeanimation) und das komplette T.S.-Design als inline CSS. Keine externen Abhängigkeiten.

- [ ] **Schritt 1: index.html erstellen**

Datei: `docs/index.html`

```html
<!DOCTYPE html>
<html lang="de">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="AI News">
  <meta name="theme-color" content="#2D362E">
  <link rel="manifest" href="manifest.json">
  <link rel="apple-touch-icon" href="icon-180.png">
  <title>AI News Briefing</title>
  <style>
    /* T.S. Corporate Design — Variablen */
    :root {
      --olive:       #2D362E;
      --olive-dark:  #3D4A3E;
      --orange:      #D97706;
      --white:       #FFFFFF;
      --gray-text:   #4B5563;
      --gray-subtle: #9CA3AF;
      --gray-light:  #F3F4F6;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Liberation Sans', Arial, sans-serif;
      background: var(--olive);
      color: var(--white);
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }

    /* ── PIN SCREEN ── */
    #pin-screen {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      min-height: 100vh;
      padding: 32px 24px;
    }

    .logo-badge {
      width: 80px; height: 80px;
      border-radius: 50%;
      background: var(--olive);
      border: 3px solid var(--orange);
      display: flex; align-items: center; justify-content: center;
      font-size: 22px; font-weight: 700;
      margin-bottom: 20px;
    }

    #pin-title { font-size: 22px; font-weight: 700; margin-bottom: 6px; }

    #pin-subtitle {
      color: var(--gray-subtle);
      font-size: 13px;
      margin-bottom: 32px;
      text-align: center;
      max-width: 240px;
    }

    .pin-dots { display: flex; gap: 16px; margin-bottom: 32px; }

    .pin-dot {
      width: 16px; height: 16px;
      border-radius: 50%;
      border: 2px solid var(--orange);
      background: transparent;
      transition: background 0.1s;
    }
    .pin-dot.filled { background: var(--orange); }

    .pin-pad {
      display: grid;
      grid-template-columns: repeat(3, 1fr);
      gap: 12px;
      width: 210px;
    }

    .pin-key {
      background: var(--olive-dark);
      border: none; border-radius: 10px;
      padding: 16px;
      color: var(--white);
      font-size: 22px; font-weight: 700;
      cursor: pointer;
      font-family: inherit;
      transition: background 0.1s;
      -webkit-tap-highlight-color: transparent;
    }
    .pin-key:active { background: var(--orange); }
    .pin-key.delete { font-size: 16px; }
    .pin-key.empty { background: transparent; cursor: default; }

    #pin-error {
      color: #EF4444;
      font-size: 12px;
      margin-top: 16px;
      min-height: 18px;
      text-align: center;
    }

    /* ── APP SCREEN ── */
    #app-screen { display: none; }

    .app-header {
      background: var(--olive);
      padding: 14px 20px;
      border-bottom: 2px solid var(--orange);
      display: flex;
      align-items: center;
      justify-content: space-between;
      position: sticky; top: 0; z-index: 10;
    }

    .header-left { display: flex; align-items: center; gap: 12px; }

    .header-badge {
      width: 40px; height: 40px; border-radius: 50%;
      background: var(--olive); border: 2px solid var(--orange);
      display: flex; align-items: center; justify-content: center;
      font-size: 11px; font-weight: 700; flex-shrink: 0;
    }

    .header-title { font-size: 15px; font-weight: 700; }
    .header-sub { color: var(--gray-subtle); font-size: 10px; margin-top: 1px; }

    .badge-privat {
      background: var(--orange); color: var(--white);
      font-size: 9px; font-weight: 700;
      padding: 3px 9px; border-radius: 10px;
    }

    .meta-bar {
      background: var(--olive-dark);
      padding: 8px 20px;
      display: flex; justify-content: space-between; align-items: center;
      flex-wrap: wrap; gap: 4px;
    }
    .meta-bar span { color: var(--gray-light); font-size: 10px; }

    .content { padding: 20px; max-width: 680px; margin: 0 auto; }

    .section-label {
      color: var(--orange);
      font-size: 9px; font-weight: 700;
      letter-spacing: 1.5px;
      margin-bottom: 14px;
    }

    #summary-text {
      color: var(--gray-light);
      font-size: 14px; line-height: 1.85;
      white-space: pre-wrap;
    }

    /* Praxis-Tipp Hervorhebung */
    .tip-box {
      background: var(--olive-dark);
      border-left: 3px solid var(--orange);
      border-radius: 6px;
      padding: 14px 16px;
      margin-top: 18px;
      font-size: 13px; line-height: 1.6;
      color: var(--gray-light);
    }

    .generate-btn {
      display: block; width: 100%;
      background: var(--orange); color: var(--white);
      border: none; border-radius: 8px;
      padding: 15px;
      font-size: 14px; font-weight: 700;
      cursor: pointer; font-family: inherit;
      margin-top: 28px;
      transition: opacity 0.2s;
      -webkit-tap-highlight-color: transparent;
    }
    .generate-btn:hover { opacity: 0.9; }
    .generate-btn:disabled { opacity: 0.45; cursor: not-allowed; }

    /* ── LOADING SCREEN ── */
    #loading-screen {
      display: none; flex-direction: column;
      align-items: center; justify-content: center;
      min-height: 60vh; padding: 40px;
    }

    .spinner {
      width: 52px; height: 52px;
      border: 3px solid var(--olive-dark);
      border-top-color: var(--orange);
      border-radius: 50%;
      animation: spin 0.8s linear infinite;
      margin-bottom: 24px;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    #loading-text {
      color: var(--gray-subtle); font-size: 14px;
      text-align: center; line-height: 1.7;
    }

    /* ── TOKEN MODAL ── */
    #token-modal {
      display: none; position: fixed; inset: 0;
      background: rgba(0,0,0,0.75);
      z-index: 100; align-items: center;
      justify-content: center; padding: 20px;
    }
    #token-modal.visible { display: flex; }

    .modal-box {
      background: var(--olive-dark); border-radius: 14px;
      padding: 26px; width: 100%; max-width: 420px;
      border: 1px solid var(--orange);
    }
    .modal-title { font-size: 17px; font-weight: 700; margin-bottom: 10px; }
    .modal-text {
      color: var(--gray-subtle); font-size: 12px;
      line-height: 1.7; margin-bottom: 16px;
    }
    .modal-text a { color: var(--orange); }
    .modal-input {
      width: 100%; background: var(--olive);
      border: 1px solid var(--orange); border-radius: 6px;
      padding: 10px 12px; color: var(--white);
      font-size: 12px; font-family: monospace;
      margin-bottom: 12px;
    }
    .modal-btn {
      background: var(--orange); color: var(--white);
      border: none; border-radius: 6px;
      padding: 11px 20px;
      font-size: 13px; font-weight: 700;
      cursor: pointer; font-family: inherit; width: 100%;
    }
  </style>
</head>
<body>

<!-- ── Screen 1: PIN ── -->
<div id="pin-screen">
  <div class="logo-badge">T.S.</div>
  <div id="pin-title">AI News Briefing</div>
  <div id="pin-subtitle">Bitte PIN eingeben</div>
  <div class="pin-dots" id="pin-dots">
    <div class="pin-dot"></div>
    <div class="pin-dot"></div>
    <div class="pin-dot"></div>
    <div class="pin-dot"></div>
  </div>
  <div class="pin-pad">
    <button class="pin-key" onclick="pinInput('1')">1</button>
    <button class="pin-key" onclick="pinInput('2')">2</button>
    <button class="pin-key" onclick="pinInput('3')">3</button>
    <button class="pin-key" onclick="pinInput('4')">4</button>
    <button class="pin-key" onclick="pinInput('5')">5</button>
    <button class="pin-key" onclick="pinInput('6')">6</button>
    <button class="pin-key" onclick="pinInput('7')">7</button>
    <button class="pin-key" onclick="pinInput('8')">8</button>
    <button class="pin-key" onclick="pinInput('9')">9</button>
    <button class="pin-key empty" disabled aria-hidden="true"></button>
    <button class="pin-key" onclick="pinInput('0')">0</button>
    <button class="pin-key delete" onclick="pinDelete()">⌫</button>
  </div>
  <div id="pin-error" role="alert"></div>
</div>

<!-- ── Screen 2: Hauptansicht ── -->
<div id="app-screen">
  <header class="app-header">
    <div class="header-left">
      <div class="header-badge">T.S.</div>
      <div>
        <div class="header-title">AI News Briefing</div>
        <div class="header-sub">Sales Engineering | KAM</div>
      </div>
    </div>
    <div class="badge-privat">PRIVAT</div>
  </header>

  <div class="meta-bar">
    <span id="meta-date">Lädt...</span>
    <span id="meta-sources"></span>
  </div>

  <!-- Screen 3: Ladeanimation (innerhalb App) -->
  <div id="loading-screen">
    <div class="spinner"></div>
    <div id="loading-text">
      Briefing wird generiert…<br>Das dauert ca. 45 Sekunden.
    </div>
  </div>

  <div class="content" id="main-content">
    <div class="section-label">AKTUELLES BRIEFING</div>
    <div id="summary-text">Lädt…</div>
    <button class="generate-btn" id="generate-btn" onclick="triggerGenerate()">
      ⟳ Briefing neu generieren
    </button>
  </div>
</div>

<!-- ── GitHub Token Modal ── -->
<div id="token-modal" role="dialog" aria-modal="true">
  <div class="modal-box">
    <div class="modal-title">🔑 GitHub Token eingeben</div>
    <div class="modal-text">
      Einmalig nötig für den manuellen Trigger. Token erstellen unter:<br>
      github.com → Settings → Developer settings →
      Personal access tokens → Fine-grained tokens<br><br>
      Berechtigung: <strong>Actions → Read &amp; Write</strong><br>
      Repository: <strong>ai-news-web</strong>
    </div>
    <input
      class="modal-input"
      type="password"
      id="token-input"
      placeholder="github_pat_..."
      autocomplete="off"
    >
    <button class="modal-btn" onclick="saveToken()">Speichern &amp; Generieren</button>
  </div>
</div>

<script src="app.js"></script>
</body>
</html>
```

- [ ] **Schritt 2: Datei lokal im Browser prüfen**

```bash
open /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web/docs/index.html
```

Erwartet: PIN-Screen mit T.S.-Badge wird angezeigt, Deep Olive Hintergrund, orange Ring.

- [ ] **Schritt 3: Commit**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
git add docs/index.html
git commit -m "feat: index.html — PWA main page, T.S. design, all 3 screens"
```

---

## Task 7: app.js — App-Logik

**Files:**
- Erstellen: `docs/app.js`

`app.js` enthält PIN-Logik, Daten laden und GitHub API Trigger. **Vor dem Commit muss `REPO_OWNER` angepasst werden.**

- [ ] **Schritt 1: app.js erstellen**

Datei: `docs/app.js`

```javascript
// ============================================================
// KONFIGURATION — MUSS ANGEPASST WERDEN
// ============================================================
// Dein GitHub-Benutzername (zu finden unter github.com/DEIN_NAME)
const REPO_OWNER = 'usa1812ts-AI';   // ← Prüfen ob korrekt
const REPO_NAME  = 'ai-news-web';

// ============================================================
// KONSTANTEN
// ============================================================
const DATA_URL   = './data/latest.json';
const PIN_KEY    = 'ts_pin_hash_v1';
const TOKEN_KEY  = 'ts_gh_token_v1';
const PIN_SALT   = 'ts-news-briefing-2026';

// ============================================================
// PIN — Hilfsfunktionen
// ============================================================

/** SHA-256 Hash des PINs (mit Salt) — nie als Klartext speichern */
async function hashPin(pin) {
  const data  = new TextEncoder().encode(pin + PIN_SALT);
  const hash  = await crypto.subtle.digest('SHA-256', data);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, '0'))
    .join('');
}

/** Aktualisiert die 4 PIN-Punkte im UI */
function updateDots(length) {
  document.querySelectorAll('.pin-dot').forEach((dot, i) => {
    dot.classList.toggle('filled', i < length);
  });
}

// ============================================================
// PIN — State
// ============================================================
let pinBuffer    = '';   // aktuell eingegebene Ziffern
let isConfirming = false; // Bestätigungs-Schritt beim ersten Festlegen
let firstPin     = '';   // erster Eingabe-Schritt beim Festlegen

// ============================================================
// PIN — Eingabe verarbeiten
// ============================================================

window.pinInput = function(digit) {
  if (pinBuffer.length >= 4) return;
  pinBuffer += digit;
  updateDots(pinBuffer.length);
  if (pinBuffer.length === 4) setTimeout(processPin, 150);
};

window.pinDelete = function() {
  pinBuffer = pinBuffer.slice(0, -1);
  updateDots(pinBuffer.length);
};

async function processPin() {
  const stored = localStorage.getItem(PIN_KEY);

  if (!stored) {
    // ── Erster Start: PIN festlegen ──
    if (!isConfirming) {
      firstPin     = pinBuffer;
      pinBuffer    = '';
      isConfirming = true;
      updateDots(0);
      document.getElementById('pin-subtitle').textContent = 'PIN bestätigen';
      document.getElementById('pin-error').textContent = '';
    } else {
      if (pinBuffer === firstPin) {
        localStorage.setItem(PIN_KEY, await hashPin(pinBuffer));
        showApp();
      } else {
        showPinError('PINs stimmen nicht überein. Bitte neu versuchen.');
        isConfirming = false;
        firstPin     = '';
        pinBuffer    = '';
        updateDots(0);
        document.getElementById('pin-subtitle').textContent =
          'Bitte lege einen PIN fest (4 Ziffern)';
      }
    }
  } else {
    // ── Einloggen ──
    const hash = await hashPin(pinBuffer);
    if (hash === stored) {
      showApp();
    } else {
      showPinError('Falscher PIN. Bitte erneut versuchen.');
      pinBuffer = '';
      updateDots(0);
    }
  }
}

function showPinError(msg) {
  const el = document.getElementById('pin-error');
  el.textContent = msg;
  setTimeout(() => { el.textContent = ''; }, 3000);
}

// ============================================================
// App anzeigen + Briefing laden
// ============================================================

function showApp() {
  document.getElementById('pin-screen').style.display = 'none';
  document.getElementById('app-screen').style.display = 'block';
  loadBriefing();
}

async function loadBriefing() {
  try {
    const res  = await fetch(DATA_URL + '?t=' + Date.now());
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();

    // Datum formatieren (MEZ/MESZ)
    const date = new Date(data.generated_at);
    const dateStr = date.toLocaleDateString('de-DE', {
      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
      timeZone: 'Europe/Berlin',
    }) + ', ' + date.toLocaleTimeString('de-DE', {
      hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Berlin',
    }) + ' Uhr';

    document.getElementById('meta-date').textContent = '📅 ' + dateStr;
    document.getElementById('meta-sources').textContent =
      (data.sources && data.sources.length)
        ? data.sources.join(' · ')
        : '';

    // Zusammenfassung rendern
    renderSummary(data.summary || '📭 Keine Daten vorhanden.');

  } catch (e) {
    document.getElementById('summary-text').textContent =
      '⚠️ Fehler beim Laden des Briefings.\nBitte Seite neu laden.\n\n' + e.message;
  }
}

/** Hebt den Praxis-Tipp orange hervor */
function renderSummary(text) {
  const el = document.getElementById('summary-text');

  const tipIndex = text.indexOf('🎯');
  if (tipIndex === -1) {
    el.textContent = text;
    return;
  }

  el.textContent = '';

  const before = document.createTextNode(text.slice(0, tipIndex));
  el.appendChild(before);

  const tipBox  = document.createElement('div');
  tipBox.className = 'tip-box';
  tipBox.textContent = text.slice(tipIndex);
  el.appendChild(tipBox);
}

// ============================================================
// Manueller Trigger via GitHub API
// ============================================================

window.triggerGenerate = async function() {
  const token = localStorage.getItem(TOKEN_KEY);
  if (!token) {
    document.getElementById('token-modal').classList.add('visible');
    return;
  }
  await dispatchWorkflow(token);
};

async function dispatchWorkflow(token) {
  const btn = document.getElementById('generate-btn');
  btn.disabled = true;
  btn.textContent = '⟳ Startet…';

  try {
    const res = await fetch(
      `https://api.github.com/repos/${REPO_OWNER}/${REPO_NAME}/actions/workflows/generate.yml/dispatches`,
      {
        method: 'POST',
        headers: {
          'Authorization':        'Bearer ' + token,
          'Accept':               'application/vnd.github+json',
          'X-GitHub-Api-Version': '2022-11-28',
          'Content-Type':         'application/json',
        },
        body: JSON.stringify({ ref: 'main' }),
      }
    );

    if (res.status === 204) {
      showLoadingScreen();
    } else {
      const err = await res.json().catch(() => ({}));
      alert(
        '❌ Trigger fehlgeschlagen: ' + (err.message || 'Status ' + res.status) +
        '\n\nBitte GitHub-Token prüfen (Actions: Read & Write).'
      );
      btn.disabled = false;
      btn.textContent = '⟳ Briefing neu generieren';
    }
  } catch (e) {
    alert('❌ Netzwerk-Fehler: ' + e.message);
    btn.disabled = false;
    btn.textContent = '⟳ Briefing neu generieren';
  }
}

function showLoadingScreen() {
  document.getElementById('main-content').style.display  = 'none';
  document.getElementById('loading-screen').style.display = 'flex';

  // Nach 75 Sek: Ankündigung, danach Seite neu laden
  setTimeout(() => {
    document.getElementById('loading-text').innerHTML =
      'Fast fertig…<br>Seite wird aktualisiert.';
    setTimeout(() => location.reload(), 8000);
  }, 75000);
}

// ============================================================
// Token speichern (aus Modal)
// ============================================================

window.saveToken = function() {
  const token = document.getElementById('token-input').value.trim();
  if (!token) {
    alert('Bitte Token eingeben.');
    return;
  }
  localStorage.setItem(TOKEN_KEY, token);
  document.getElementById('token-modal').classList.remove('visible');
  dispatchWorkflow(token);
};

// Klick außerhalb des Modals schließt es
document.getElementById('token-modal').addEventListener('click', function(e) {
  if (e.target === this) this.classList.remove('visible');
});

// ============================================================
// Init
// ============================================================
window.addEventListener('load', () => {
  // Erster Start: PIN-Festlegen-Modus
  if (!localStorage.getItem(PIN_KEY)) {
    document.getElementById('pin-title').textContent    = 'Willkommen!';
    document.getElementById('pin-subtitle').textContent =
      'Bitte lege einen PIN fest (4 Ziffern)';
  }

  // Service Worker registrieren
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.register('./service-worker.js').catch(console.warn);
  }
});
```

- [ ] **Schritt 2: REPO_OWNER prüfen**

Öffne `docs/app.js` und prüfe Zeile 6:
```javascript
const REPO_OWNER = 'usa1812ts-AI';
```
Das muss dein exakter GitHub-Benutzername sein. Prüfen unter: github.com → rechts oben auf dein Profilbild klicken → "Your profile" → der Name in der URL.

- [ ] **Schritt 3: Lokal im Browser testen**

```bash
# Einfacher lokaler Webserver (Python eingebaut)
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web/docs
python3 -m http.server 8080
```

Browser öffnen: `http://localhost:8080`

Testen:
1. PIN-Screen erscheint mit T.S.-Badge
2. Einen 4-stelligen PIN eingeben (z.B. 1234) → wird "gesetzt"
3. PIN nochmal eingeben → Hauptansicht erscheint
4. Briefing-Text aus `docs/data/latest.json` wird angezeigt
5. Praxis-Tipp (🎯) wird orange hervorgehoben

Mit `Ctrl+C` den Server stoppen.

- [ ] **Schritt 4: localStorage leeren für sauberen Test**

Im Browser: DevTools (Cmd+Option+I) → Application → Local Storage → alle Einträge löschen → Seite neu laden → PIN-Setup erscheint wieder.

- [ ] **Schritt 5: Commit**

```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
git add docs/app.js
git commit -m "feat: app.js — PIN auth, briefing load, GitHub API trigger"
```

---

## Task 8: GitHub Repository einrichten und live schalten

**Voraussetzungen:** GitHub-Konto (usa1812ts-AI), GitHub CLI installiert oder Browser-Zugang.

- [ ] **Schritt 1: Neues öffentliches Repo auf GitHub erstellen**

Option A — Terminal (GitHub CLI):
```bash
# Einmalig einloggen falls nötig:
gh auth login

cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
gh repo create ai-news-web --public --source=. --remote=origin --push
```

Option B — Browser:
1. github.com → "New repository"
2. Name: `ai-news-web`
3. Sichtbarkeit: **Public**
4. Kein README hinzufügen (haben wir schon Inhalt)
5. "Create repository"

Dann im Terminal:
```bash
cd /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-web
git remote add origin https://github.com/usa1812ts-AI/ai-news-web.git
git branch -M main
git push -u origin main
```

- [ ] **Schritt 2: GitHub Pages aktivieren**

1. github.com/usa1812ts-AI/ai-news-web → "Settings"
2. Linke Sidebar: "Pages"
3. Source: **Deploy from a branch**
4. Branch: **main** / Folder: **/docs**
5. "Save"

Warte ca. 2 Minuten. Die URL erscheint dann oben:
`https://usa1812ts-ai.github.io/ai-news-web/`

- [ ] **Schritt 3: GitHub Secrets hinzufügen**

github.com/usa1812ts-AI/ai-news-web → Settings → Secrets and variables → Actions → "New repository secret"

Folgende Secrets anlegen:

| Secret-Name | Wert | Quelle |
|---|---|---|
| `OPENAI_API_KEY` | dein OpenAI API Key | platform.openai.com → API keys |
| `GMAIL_TOKEN_JSON` | Inhalt von `token.json` | `cat /Users/thomas/Downloads/ClaudeCodeTerminal/ai-news-agent/token.json` |

**Wichtig:** Der `GMAIL_TOKEN_JSON`-Inhalt ist die gesamte JSON-Datei als Text (geschweifte Klammern einschließen).

- [ ] **Schritt 4: Ersten manuellen Workflow-Lauf starten**

github.com/usa1812ts-AI/ai-news-web → "Actions" → "AI News Briefing generieren" → "Run workflow" → "Run workflow"

Den Lauf beobachten (grüner Haken = Erfolg). Dauert ca. 1–2 Minuten.

- [ ] **Schritt 5: PWA im Browser prüfen**

URL öffnen: `https://usa1812ts-ai.github.io/ai-news-web/`

Prüfen:
1. PIN-Screen erscheint
2. Nach PIN-Eingabe: echte Zusammenfassung sichtbar
3. Datum und Quellen in der Meta-Leiste korrekt
4. Praxis-Tipp orange hervorgehoben

- [ ] **Schritt 6: PWA auf iPhone installieren**

1. Safari auf iPhone → `https://usa1812ts-ai.github.io/ai-news-web/`
2. Teilen-Symbol (Quadrat mit Pfeil nach oben)
3. "Zum Home-Bildschirm hinzufügen"
4. App-Icon mit T.S.-Badge erscheint auf dem Homescreen
5. Öffnen → App startet ohne Browser-Leiste (Standalone-Modus)

- [ ] **Schritt 7: "Neu generieren"-Button testen**

1. Einen GitHub Personal Access Token erstellen:
   - github.com → Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Repository: `ai-news-web` (nur dieses)
   - Berechtigung: **Actions → Read & Write**
   - Token kopieren (beginnt mit `github_pat_...`)

2. In der App: "⟳ Briefing neu generieren" drücken
3. Token im Modal eingeben → "Speichern & Generieren"
4. Ladeanimation erscheint (~75 Sek)
5. Seite lädt automatisch neu mit frischem Briefing

---

## Checkliste: Go-Live Kriterien

- [ ] GitHub Pages URL ist erreichbar
- [ ] PIN-Schutz funktioniert (kein Zugang ohne PIN)
- [ ] Täglicher Cron läuft (morgen um 18:00 Uhr prüfen)
- [ ] Manueller Trigger funktioniert
- [ ] PWA auf iPhone installierbar
- [ ] `ai-news-agent` (Telegram) läuft weiterhin unverändert
