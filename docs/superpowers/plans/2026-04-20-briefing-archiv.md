# Briefing-Archiv Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Die letzten 7 Briefings in einer `archive.json` speichern und per Archiv-Button 🗂️ in der PWA abrufbar machen.

**Architecture:** `generate.py` befüllt `docs/data/archive.json` bei jedem Lauf. Die PWA lädt diese Datei bei Bedarf und zeigt eine navigierbare Liste + Detailansicht an. Navigation erfolgt über einen neuen Header-Button.

**Tech Stack:** Python 3.11 (Backend), Vanilla JS / HTML / CSS (PWA), GitHub Actions (CI)

---

## Datei-Übersicht

| Datei | Aktion | Zweck |
|---|---|---|
| `generate.py` | Modifizieren | archive.json befüllen |
| `.github/workflows/generate.yml` | Modifizieren | archive.json committen |
| `docs/index.html` | Modifizieren | Archiv-Button + Archiv-Screens |
| `docs/app.js` | Modifizieren | Archiv-Logik + Navigation |
| `docs/data/archive.json` | Wird generiert | Datenhaltung (nicht manuell bearbeiten) |

---

## Task 1: Backend — archive.json in generate.py

**Files:**
- Modify: `generate.py:55-76`

- [ ] **Schritt 1: archive.json-Logik nach dem latest.json-Schreibvorgang einfügen**

In `generate.py`, den Block `# Schritt 3: JSON schreiben...` erweitern. Ersetze den gesamten Schritt-3-Block (Zeile 55–71) durch:

```python
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
```

- [ ] **Schritt 2: Ausgabe am Ende anpassen**

Die Abschluss-Ausgabe bleibt unverändert — kein Handlungsbedarf.

- [ ] **Schritt 3: Manuell testen (lokal)**

```bash
cd /Users/tsaispace/ClaudeCodeTerminal/ai-news-web
python generate.py
```

Erwartetes Ergebnis in der Ausgabe:
```
📚 Schritt 4: Archiv aktualisieren...
   ✅ docs/data/archive.json aktualisiert (1 Einträge)
```

Prüfen ob Datei erstellt wurde:
```bash
cat docs/data/archive.json
```

Erwartete Ausgabe: JSON-Array mit einem Objekt (date, generated_at, summary).

- [ ] **Schritt 4: Commit**

```bash
git add generate.py
git commit -m "feat: archive.json in generate.py befüllen (letzte 7 Briefings)"
```

---

## Task 2: Workflow — archive.json committen

**Files:**
- Modify: `.github/workflows/generate.yml:39`

- [ ] **Schritt 1: git add im Workflow erweitern**

In `.github/workflows/generate.yml` den Step `Ergebnis committen und pushen` anpassen.

Alte Zeile:
```yaml
          git add docs/data/latest.json
```

Neue Zeile:
```yaml
          git add docs/data/latest.json docs/data/archive.json
```

- [ ] **Schritt 2: Commit**

```bash
git add .github/workflows/generate.yml
git commit -m "feat: archive.json im Workflow committen"
```

---

## Task 3: HTML — Archiv-Button und Archiv-Screens

**Files:**
- Modify: `docs/index.html`

- [ ] **Schritt 1: Archiv-Button im Header einfügen**

In `docs/index.html`, den `header-right`-Div (Zeile 294–298) ersetzen durch:

```html
    <div class="header-right">
      <div class="badge-privat">PRIVAT</div>
      <button class="settings-btn" id="archive-btn" onclick="openArchive()" title="Archiv">🗂️</button>
      <button class="settings-btn" id="back-btn" onclick="closeArchive()" title="Zurück" style="display:none">← Zurück</button>
      <button class="settings-btn" onclick="openSettings()" title="Einstellungen">⚙️</button>
    </div>
```

- [ ] **Schritt 2: Archiv-Listen-Screen als neuen div einfügen**

Direkt nach `<div class="content" id="main-content">` (vor dem schließenden `</div>` des app-screen) einfügen:

```html
  <!-- ── Screen: Archiv-Liste ── -->
  <div class="content" id="archive-screen" style="display:none">
    <div class="section-label">ARCHIV — LETZTE 7 TAGE</div>
    <div id="archive-list"></div>
  </div>
```

- [ ] **Schritt 3: CSS für Archiv-Liste in den `<style>`-Block einfügen**

Am Ende des `<style>`-Blocks (vor `</style>`) einfügen:

```css
    /* ── ARCHIV ── */
    .archive-item {
      background: var(--olive-dark);
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 12px;
      cursor: pointer;
      border: 1px solid transparent;
      transition: border-color 0.15s;
    }
    .archive-item:active { border-color: var(--orange); }

    .archive-item-date {
      font-size: 13px;
      font-weight: 700;
      color: var(--white);
      margin-bottom: 4px;
    }

    .archive-item-preview {
      font-size: 11px;
      color: var(--gray-subtle);
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .archive-today-badge {
      background: var(--orange);
      color: var(--white);
      font-size: 9px;
      font-weight: 700;
      padding: 2px 7px;
      border-radius: 8px;
      margin-left: 8px;
      vertical-align: middle;
    }

    .back-btn-label { font-size: 13px; }
```

- [ ] **Schritt 4: Commit**

```bash
git add docs/index.html
git commit -m "feat: Archiv-Button und Archiv-Screen in index.html"
```

---

## Task 4: JavaScript — Archiv-Logik in app.js

**Files:**
- Modify: `docs/app.js`

- [ ] **Schritt 1: Archiv-Konstante und Cache-Variable hinzufügen**

Nach Zeile 11 (`const PIN_SALT = ...`) einfügen:

```js
const ARCHIVE_URL = './data/archive.json';
let archiveCache  = null;
```

- [ ] **Schritt 2: `openArchive()`-Funktion hinzufügen**

Am Ende von `app.js` (vor dem `window.addEventListener('load', ...)`) einfügen:

```js
// ============================================================
// Archiv
// ============================================================

window.openArchive = async function() {
  document.getElementById('main-content').style.display   = 'none';
  document.getElementById('archive-screen').style.display = 'block';
  document.getElementById('archive-btn').style.display    = 'none';
  document.getElementById('back-btn').style.display       = 'inline-block';

  if (!archiveCache) {
    try {
      const res = await fetch(ARCHIVE_URL + '?t=' + Date.now());
      if (!res.ok) throw new Error('HTTP ' + res.status);
      archiveCache = await res.json();
    } catch (e) {
      document.getElementById('archive-list').innerHTML =
        '<p style="color:var(--gray-subtle);font-size:13px">⚠️ Archiv konnte nicht geladen werden.</p>';
      return;
    }
  }

  renderArchiveList(archiveCache);
};

function renderArchiveList(entries) {
  const container = document.getElementById('archive-list');
  if (!entries || entries.length === 0) {
    container.innerHTML =
      '<p style="color:var(--gray-subtle);font-size:13px">Noch keine archivierten Briefings.</p>';
    return;
  }

  container.innerHTML = '';
  const todayStr = new Date().toISOString().slice(0, 10);

  entries.forEach((entry, index) => {
    const isToday = entry.date === todayStr;
    const dateObj = new Date(entry.generated_at);
    const dateLabel = dateObj.toLocaleDateString('de-DE', {
      weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
      timeZone: 'Europe/Berlin',
    });
    const preview = (entry.summary || '').replace(/\n/g, ' ').slice(0, 80) + '…';

    const item = document.createElement('div');
    item.className = 'archive-item';
    item.innerHTML = `
      <div class="archive-item-date">
        ${dateLabel}${isToday ? '<span class="archive-today-badge">Heute</span>' : ''}
      </div>
      <div class="archive-item-preview">${preview}</div>
    `;
    item.addEventListener('click', () => showArchiveDetail(entry));
    container.appendChild(item);
  });
}

function showArchiveDetail(entry) {
  document.getElementById('archive-screen').style.display = 'none';
  document.getElementById('main-content').style.display   = 'block';
  document.getElementById('generate-btn').style.display   = 'none';

  const dateObj  = new Date(entry.generated_at);
  const dateStr  = dateObj.toLocaleDateString('de-DE', {
    weekday: 'long', day: 'numeric', month: 'long', year: 'numeric',
    timeZone: 'Europe/Berlin',
  }) + ', ' + dateObj.toLocaleTimeString('de-DE', {
    hour: '2-digit', minute: '2-digit', timeZone: 'Europe/Berlin',
  }) + ' Uhr';

  document.getElementById('meta-date').textContent = '📅 ' + dateStr;
  renderSummary(entry.summary || '📭 Kein Inhalt vorhanden.');
}

window.closeArchive = function() {
  document.getElementById('archive-screen').style.display = 'none';
  document.getElementById('main-content').style.display   = 'block';
  document.getElementById('generate-btn').style.display   = 'block';
  document.getElementById('archive-btn').style.display    = 'inline-block';
  document.getElementById('back-btn').style.display       = 'none';

  // Aktuelles Briefing wiederherstellen
  loadBriefing();
};
```

- [ ] **Schritt 3: Commit**

```bash
git add docs/app.js
git commit -m "feat: Archiv-Logik in app.js (openArchive, renderArchiveList, showArchiveDetail)"
```

---

## Task 5: Push und Abschlusstest

- [ ] **Schritt 1: Alle Änderungen auf GitHub pushen**

```bash
git push
```

- [ ] **Schritt 2: PWA im Browser testen**

GitHub Pages URL aufrufen → PIN eingeben → 🗂️-Button antippen.

Erwartetes Verhalten:
- Archiv-Liste erscheint mit Datum und Vorschau
- Eintrag antippen → volles Briefing wird angezeigt
- "← Zurück" antippen → zurück zur Liste
- Zahnrad ⚙️ bleibt immer sichtbar und funktioniert

- [ ] **Schritt 3: Workflow manuell triggern**

"Briefing neu generieren" antippen → nach Abschluss prüfen ob `archive.json` auf GitHub aktualisiert wurde.

Prüfen unter: `github.com/usa1812ts-AI/ai-news-web/blob/main/docs/data/archive.json`
