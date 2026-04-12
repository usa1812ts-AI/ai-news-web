# Design Spec: AI News Web App (PWA)

**Datum:** 12. April 2026  
**Projekt:** ai-news-web  
**Status:** Approved

---

## Ziel

Aufbau einer privaten Progressive Web App (PWA), die dieselben KI-Newsletter-Zusammenfassungen wie der bestehende `ai-news-agent` (Telegram) als Web-Oberfläche darstellt — erreichbar via Internet auf Mac, iPad und iPhone. Das bestehende Telegram-Projekt bleibt vollständig unberührt und läuft parallel weiter.

---

## Anforderungen

- **Zugang:** Nur für den Eigentümer (T.S.), passwortgeschützt via 4-stelligem PIN
- **Geräte:** Mac (Browser), iPad, iPhone (als installierbare PWA)
- **Hosting:** 100% GitHub (GitHub Pages + GitHub Actions) — kein externes Hosting
- **Design:** T.S. Corporate Design System (Deep Olive + Muted Orange)
- **Funktion:** Zusammenfassung lesen + manuell neu auslösen
- **Telegram:** Bleibt parallel aktiv, kein Eingriff in `ai-news-agent`

---

## Architektur

```
[GitHub Actions: generate.yml]
  ├── Trigger: täglich 18:00 MEZ (cron) ODER manuell (workflow_dispatch)
  ├── Schritt 1: gmail_reader.py  → Newsletter aus Gmail holen
  ├── Schritt 2: summarizer.py   → Claude/OpenAI API → Zusammenfassung
  └── Schritt 3: Ergebnis in data/latest.json schreiben + committen

[GitHub Pages]
  └── Hostet web/ als statische PWA (öffentliches Repo, kein kostenpflichtiges Pro nötig)

[PWA im Browser]
  ├── Lädt data/latest.json und zeigt Zusammenfassung an
  ├── PIN-Schutz beim ersten Öffnen (gespeichert in localStorage)
  ├── GitHub Token einmalig eingeben (gespeichert in localStorage) → für manuellen Trigger
  └── "Neu generieren"-Button → GitHub API workflow_dispatch → Actions startet
```

---

## Projektstruktur

```
ai-news-web/
├── .github/
│   └── workflows/
│       └── generate.yml           # Cron + manueller Trigger, schreibt latest.json
├── data/
│   └── latest.json                # Aktuelle Zusammenfassung (von Actions befüllt)
├── web/
│   ├── index.html                 # PWA Hauptseite (T.S. Design)
│   ├── app.js                     # Logik: laden, PIN, GitHub API trigger
│   ├── manifest.json              # PWA: Installierbar auf iPhone/iPad
│   └── service-worker.js          # PWA: Offline-Fähigkeit (Cache)
├── gmail_reader.py                # Übernommen aus ai-news-agent
├── summarizer.py                  # Übernommen aus ai-news-agent
├── requirements.txt               # Python-Abhängigkeiten
├── .gitignore
└── docs/
    └── superpowers/
        └── specs/
            └── 2026-04-12-ai-news-web-design.md
```

---

## Datenformat: data/latest.json

```json
{
  "generated_at": "2026-04-12T18:04:00+02:00",
  "sources": ["The Rundown AI", "The Neuron", "Superhuman"],
  "summary": "🤖 AI News Briefing\n📅 12. April 2026...",
  "audio_available": false
}
```

---

## UI: Screens

### Screen 1 — PIN-Eingabe (erster Start)
- T.S. Logo-Badge (CSS, kein Bild nötig) zentriert
- 4 Kreise als PIN-Indikator
- Numpad (0–9 + Löschen)
- PIN wird in `localStorage` gehasht gespeichert
- Nach korrekter Eingabe: Weiterleitung zur Hauptansicht

### Screen 2 — Hauptansicht
- **Header:** T.S. Badge + "AI News Briefing" + "PRIVAT"-Badge (orange)
- **Meta-Leiste:** Datum, Uhrzeit MEZ, Anzahl Meldungen
- **Inhalt:** Zusammenfassung als Stichpunkte, Praxis-Tipp orange hervorgehoben
- **Button:** "⟳ Briefing neu generieren" (Deep Olive auf Desktop, Orange auf Mobile)
- **Desktop-Sidebar:** Quellen-Liste, letzter Lauf-Zeitstempel

### Screen 3 — Ladeansicht (während Generierung)
- Spinner im T.S.-Stil
- Text: "Briefing wird generiert... (~45 Sekunden)"
- Automatisches Neuladen nach 60 Sekunden

---

## Sicherheit

| Maßnahme | Detail |
|---|---|
| PIN-Schutz | 4-stellig, gehashter Vergleich in localStorage |
| GitHub Token | Einmalig eingeben, in localStorage gespeichert, nur für workflow_dispatch |
| Repo-Sichtbarkeit | Öffentlich (nötig für kostenlose GitHub Pages), aber ohne direkten Link nicht auffindbar |
| Secrets in Actions | ANTHROPIC_API_KEY, OPENAI_API_KEY, GMAIL_TOKEN_JSON, GMAIL_CREDENTIALS_JSON |

---

## GitHub Actions: generate.yml (Logik)

```
Trigger:
  - schedule: cron '0 17 * * *'  (= 18:00 MEZ)
  - workflow_dispatch              (= manueller Trigger via App oder GitHub UI)

Schritte:
  1. Python-Umgebung aufsetzen + requirements.txt installieren
  2. Gmail-Credentials aus Secrets in Dateien schreiben
  3. gmail_reader.py ausführen
  4. summarizer.py ausführen
  5. latest.json schreiben
  6. Commit + Push (data/latest.json) ins Repo
```

---

## PWA-Konfiguration

- `manifest.json`: App-Name "AI News", Icons (T.S. Badge), Theme-Color `#2D362E`
- `service-worker.js`: Cache von `index.html`, `app.js`, `manifest.json` für Offline-Anzeige der letzten Zusammenfassung
- iOS: `apple-touch-icon` + `apple-mobile-web-app-capable` Meta-Tags

---

## Nicht im Scope (Phase 1)

- Benutzer-Verwaltung / mehrere Accounts
- Push-Benachrichtigungen (kann in Phase 2 ergänzt werden)
- Historische Zusammenfassungen / Archiv
- TTS-Audio direkt in der App (Telegram bleibt für Audio)
- Eigene Domain (github.io reicht für Phase 1)
