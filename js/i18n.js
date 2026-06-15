// Simple i18n engine
const lang = localStorage.getItem('lang') || (navigator.language.startsWith('zh') ? 'zh' : 'en');
let t = i18n[lang];

function setLang(l) {
  localStorage.setItem('lang', l);
  location.reload();
}

function tr(key, fallback = '') {
  const keys = key.split('.');
  let val = t;
  for (const k of keys) { if (val && val[k] !== undefined) val = val[k]; else return fallback || key; }
  return val || fallback || key;
}

function applyI18n() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    const text = tr(key);
    if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') el.placeholder = text;
    else el.textContent = text;
  });
  document.querySelectorAll('[data-i18n-title]').forEach(el => {
    el.title = tr(el.getAttribute('data-i18n-title'));
  });
}

document.addEventListener('DOMContentLoaded', () => {
  applyI18n();
  const switchBtn = document.getElementById('lang-switch');
  if (switchBtn) {
    switchBtn.textContent = tr('langSwitch');
    switchBtn.onclick = () => setLang(lang === 'zh' ? 'en' : 'zh');
  }
});
