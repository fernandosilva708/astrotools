/**
 * i18n.js - Simple translation engine for AstroTools
 */

function getLanguage() {
    return localStorage.getItem('language') || navigator.language.split('-')[0] || 'pt';
}

function setLanguage(lang) {
    if (TRANSLATIONS[lang]) {
        localStorage.setItem('language', lang);
        applyTranslations();
        document.documentElement.lang = lang;
        location.reload();
    }
}

function t(key) {
    const lang = getLanguage();
    return (TRANSLATIONS[lang] && TRANSLATIONS[lang][key]) || key;
}

function applyTranslations() {
    const lang = getLanguage();
    const texts = TRANSLATIONS[lang] || TRANSLATIONS['pt'];
    
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        if (texts[key]) {
            if (el.tagName === 'INPUT' && (el.type === 'placeholder' || el.getAttribute('placeholder'))) {
                el.placeholder = texts[key];
            } else if (el.tagName === 'OPTGROUP' || el.tagName === 'OPTION') {
                el.text = texts[key];
            } else {
                // Preservar elementos filhos (como inputs dentro de labels)
                // Procura o primeiro nó de texto
                let textNode = Array.from(el.childNodes).find(node => node.nodeType === Node.TEXT_NODE);
                if (textNode) {
                    textNode.textContent = texts[key];
                } else {
                    // Se não houver nó de texto, insere no início
                    el.prepend(document.createTextNode(texts[key]));
                }
            }
        }
    });
}

// Initial application
document.addEventListener('DOMContentLoaded', () => {
    applyTranslations();
    document.documentElement.lang = getLanguage();
});
