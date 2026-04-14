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
    openSettings();
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
// Einstellungen: Token speichern / entfernen / anzeigen
// ============================================================

window.openSettings = function() {
  const token = localStorage.getItem(TOKEN_KEY);
  const statusEl = document.getElementById('token-status');
  if (token) {
    statusEl.innerHTML = '✅ <strong style="color:#4ade80">Token gespeichert</strong> — du kannst ihn hier ändern oder entfernen.';
    document.getElementById('token-input').value = '';
    document.getElementById('token-input').placeholder = 'Neuen Token eingeben (leer lassen = behalten)';
  } else {
    statusEl.innerHTML = '⚠️ <strong style="color:#fb923c">Kein Token hinterlegt</strong> — bitte einmalig eingeben.';
    document.getElementById('token-input').value = '';
    document.getElementById('token-input').placeholder = 'github_pat_...';
  }
  document.getElementById('token-modal').classList.add('visible');
};

window.saveToken = function() {
  const input = document.getElementById('token-input').value.trim();
  const existing = localStorage.getItem(TOKEN_KEY);

  if (!input && !existing) {
    alert('Bitte Token eingeben.');
    return;
  }

  if (input) {
    localStorage.setItem(TOKEN_KEY, input);
    document.getElementById('token-modal').classList.remove('visible');
    dispatchWorkflow(input);
  } else {
    // Kein neuer Token eingegeben, aber alter ist noch da → einfach schließen
    document.getElementById('token-modal').classList.remove('visible');
  }
};

window.deleteToken = function() {
  if (confirm('GitHub Token wirklich entfernen? Du musst ihn dann neu eingeben.')) {
    localStorage.removeItem(TOKEN_KEY);
    document.getElementById('token-modal').classList.remove('visible');
  }
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
