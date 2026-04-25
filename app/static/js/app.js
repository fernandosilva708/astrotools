// SPDX-License-Identifier: GPL-2.0-only
// Utilitários de frontend do AstroTools

(function () {
  const LANG_LABELS = {
    bg:'BG', cs:'CS', hr:'HR', da:'DA', sk:'SK', sl:'SL', et:'ET', fi:'FI',
    fr:'FR', el:'EL', hu:'HU', en:'EN', ga:'GA', it:'IT', lv:'LV', lt:'LT',
    mt:'MT', nl:'NL', pl:'PL', pt:'PT', ro:'RO', de:'DE', es:'ES', sv:'SV'
  };

  function t(key) {
    const lang = localStorage.getItem('ui-lang') || 'pt';
    const dict = (typeof TRANSLATIONS !== 'undefined' && TRANSLATIONS[lang]) || {};
    const fallback = (typeof TRANSLATIONS !== 'undefined' && TRANSLATIONS['pt']) || {};
    return dict[key] || fallback[key] || key;
  }

  window._t = t;

  function applyTranslations() {
    document.querySelectorAll('[data-i18n]').forEach(el => {
      el.textContent = t(el.dataset.i18n);
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      el.placeholder = t(el.dataset.i18nPlaceholder);
    });
  }

  function setLang(lang) {
    localStorage.setItem('ui-lang', lang);
    document.documentElement.lang = lang;
    const label = document.getElementById('lang-label');
    if (label) label.textContent = LANG_LABELS[lang] || lang.toUpperCase();
    document.querySelectorAll('.lang-option').forEach(el => {
      el.classList.toggle('active', el.dataset.lang === lang);
    });
    applyTranslations();
  }

  document.addEventListener('DOMContentLoaded', function () {
    const saved = localStorage.getItem('ui-lang') || 'pt';
    setLang(saved);
    
    // Suporte para o novo selector (Editorial Sidebar)
    const langSelector = document.getElementById('lang-selector');
    if (langSelector) {
        langSelector.value = saved;
        langSelector.addEventListener('change', function() {
            setLang(this.value);
        });
    }

    // Mantém compatibilidade com links antigos (se houver)
    document.querySelectorAll('.lang-option').forEach(el => {
      el.addEventListener('click', function (e) {
        e.preventDefault();
        setLang(this.dataset.lang);
        if (langSelector) langSelector.value = this.dataset.lang;
      });
    });
  });
})();
