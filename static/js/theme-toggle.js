/**
 * Toggle de tema claro/escuro
 * Persiste no localStorage e respeita prefers-color-scheme
 */
(function () {
    'use strict';

    const STORAGE_KEY = 'theme-preference';
    const html = document.documentElement;
    const announcer = document.getElementById('theme-announcer');

    function getSystemTheme() {
        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    }

    function getSavedTheme() {
        return localStorage.getItem(STORAGE_KEY);
    }

    function applyTheme(theme) {
        html.setAttribute('data-theme', theme);
        localStorage.setItem(STORAGE_KEY, theme);

        // Atualizar ícones do botão
        const sunIcon = document.getElementById('icon-sun');
        const moonIcon = document.getElementById('icon-moon');
        if (sunIcon && moonIcon) {
            if (theme === 'dark') {
                sunIcon.classList.remove('hidden');
                moonIcon.classList.add('hidden');
            } else {
                sunIcon.classList.add('hidden');
                moonIcon.classList.remove('hidden');
            }
        }

        // Anunciar troca para leitores de tela
        if (announcer) {
            announcer.textContent = theme === 'dark' ? 'Tema escuro ativado' : 'Tema claro ativado';
        }
    }

    function toggleTheme() {
        const current = html.getAttribute('data-theme') || 'light';
        applyTheme(current === 'dark' ? 'light' : 'dark');
    }

    // Inicialização
    const saved = getSavedTheme();
    applyTheme(saved || getSystemTheme());

    // Ouvir mudança do sistema
    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', function (e) {
        if (!getSavedTheme()) {
            applyTheme(e.matches ? 'dark' : 'light');
        }
    });

    // Expor globalmente
    window.toggleTheme = toggleTheme;
})();
