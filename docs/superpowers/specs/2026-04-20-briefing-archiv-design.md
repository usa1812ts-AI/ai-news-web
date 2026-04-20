# Design: Briefing-Archiv

**Datum:** 2026-04-20  
**Projekt:** ai-news-web (GitHub Pages PWA)  
**Status:** Genehmigt

---

## Ziel

Die letzten 7 Briefings sollen in der PWA abrufbar sein. Nutzer kann ältere Briefings per Archiv-Button im Header aufrufen und einzeln ansehen.

---

## Backend

### `generate.py`
- Lädt beim Start `docs/data/archive.json` (falls vorhanden)
- Fügt neues Briefing als erstes Element ein
- Kürzt Liste auf maximal 7 Einträge
- Speichert aktualisierte `archive.json`

### `archive.json` — Struktur
```json
[
  { "date": "2026-04-20", "generated_at": "2026-04-20T17:00:00Z", "summary": "..." },
  { "date": "2026-04-19", "generated_at": "2026-04-19T17:00:00Z", "summary": "..." }
]
```

### GitHub Actions (`generate.yml`)
- `archive.json` wird zusammen mit `latest.json` committed und gepusht
- Kein zusätzlicher Workflow-Schritt nötig

---

## Frontend (PWA)

### Header
- Neues Icon 🗂️ links neben dem Zahnrad ⚙️
- Öffnet die Archiv-Listenansicht

### Archiv-Listenansicht
- Zeigt die letzten 7 Einträge aus `archive.json`
- Pro Eintrag: Wochentag + Datum (z.B. "Sonntag, 20. April 2026")
- Erster Eintrag erhält Badge "Heute"
- Antippen → Briefing-Detailansicht

### Briefing-Detailansicht (Archiv)
- Gleiche Darstellung wie normale Briefing-Ansicht
- Zurück-Button im Header (ersetzt 🗂️-Icon)
- Kein "Briefing neu generieren"-Button in der Archiv-Detailansicht

### Datenfluss
```
App startet       → lädt latest.json (unverändert)
🗂️ antippen      → lädt archive.json (einmalig, gecacht)
Eintrag antippen  → zeigt summary aus archive.json
Zurück antippen   → zeigt aktuelles Briefing
```

---

## Nicht verändert
- PIN-Logik
- Token / Einstellungen-Modal
- Service Worker
- `latest.json` (bleibt unverändert)

---

## Erfolgskriterien
- Archiv-Button erscheint im Header
- Liste zeigt korrekte Daten der letzten 7 Tage
- Älteres Briefing öffnet sich mit vollem Text
- Zurück-Navigation funktioniert
- `generate.py` befüllt `archive.json` korrekt bei jedem Lauf
