let currentJobId = null;
let pollTimer = null;

const THEME_STORAGE_KEY = 'email_extractor_theme';

const el = (id) => document.getElementById(id);

function setHidden(id, hidden) {
  const node = el(id);
  if (!node) return;
  node.classList.toggle('hidden', hidden);
}

function applyTheme(theme) {
  const isDark = theme === 'dark';
  document.body.classList.toggle('dark', isDark);
  const toggle = el('dark_mode');
  if (toggle) toggle.checked = isDark;
}

function loadTheme() {
  const stored = localStorage.getItem(THEME_STORAGE_KEY);
  if (stored === 'dark' || stored === 'light') return stored;
  const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
  return prefersDark ? 'dark' : 'light';
}

function saveTheme(theme) {
  localStorage.setItem(THEME_STORAGE_KEY, theme);
}

function showError(message) {
  const node = el('error');
  node.textContent = message || '';
  node.classList.toggle('hidden', !message);
}

function resetUI() {
  showError('');
  setHidden('progress_section', true);
  setHidden('results', true);
  setHidden('no_results', true);
  el('progress_fill').style.width = '0%';
  el('progress_value').textContent = '0%';
  el('log').value = '';
  el('emails_text').value = '';
  el('metric_emails').textContent = '0';
  el('metric_text').textContent = '0';
  el('metric_pages').textContent = '0';
  el('metric_keywords').textContent = '-';
  currentJobId = null;
  if (pollTimer) {
    clearInterval(pollTimer);
    pollTimer = null;
  }
}

async function startJob() {
  resetUI();

  const keywords = el('keywords').value || '';
  const maxPages = parseInt(el('max_pages').value || '2', 10);
  const headlessMode = el('headless_mode').checked;
  const excludeFreeEmails = el('exclude_free_emails').checked;

  try {
    const resp = await fetch('/api/start', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        keywords: keywords,
        max_pages: maxPages,
        headless_mode: headlessMode,
        exclude_free_emails: excludeFreeEmails,
      }),
    });

    if (!resp.ok) {
      const data = await resp.json().catch(() => null);
      throw new Error((data && data.detail) ? data.detail : 'Failed to start');
    }

    const data = await resp.json();
    currentJobId = data.job_id;

    setHidden('progress_section', false);
    pollTimer = setInterval(pollStatus, 800);
    await pollStatus();
  } catch (e) {
    showError(e.message || String(e));
  }
}

async function pollStatus() {
  if (!currentJobId) return;

  try {
    const resp = await fetch(`/api/status/${currentJobId}`);
    if (!resp.ok) return;
    const data = await resp.json();

    const p = Math.max(0, Math.min(100, data.progress || 0));
    el('progress_fill').style.width = `${p}%`;
    el('progress_value').textContent = `${p}%`;

    el('log').value = (data.logs || []).join('\n');

    if (data.status === 'error') {
      showError(data.error || 'An error occurred');
      if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
      }
      return;
    }

    if (data.status === 'done') {
      if (pollTimer) {
        clearInterval(pollTimer);
        pollTimer = null;
      }

      const emails = data.emails_found || [];

      el('metric_emails').textContent = String(emails.length);
      el('metric_text').textContent = String(data.scraped_text_length || 0);
      el('metric_pages').textContent = String(data.max_pages || 0);
      el('metric_keywords').textContent = data.keywords || '-';

      if (emails.length > 0) {
        el('emails_text').value = emails.join('\n');
        el('download_xlsx').href = `/download/${currentJobId}/xlsx`;
        el('download_csv').href = `/download/${currentJobId}/csv`;
        el('download_txt').href = `/download/${currentJobId}/txt`;
        setHidden('results', false);
        setHidden('no_results', true);
      } else {
        setHidden('results', true);
        setHidden('no_results', false);
      }

      return;
    }
  } catch (e) {
  }
}

window.addEventListener('DOMContentLoaded', () => {
  const initialTheme = loadTheme();
  applyTheme(initialTheme);

  const darkToggle = el('dark_mode');
  if (darkToggle) {
    darkToggle.addEventListener('change', () => {
      const theme = darkToggle.checked ? 'dark' : 'light';
      applyTheme(theme);
      saveTheme(theme);
    });
  }

  el('start').addEventListener('click', startJob);
  el('clear').addEventListener('click', resetUI);
});
