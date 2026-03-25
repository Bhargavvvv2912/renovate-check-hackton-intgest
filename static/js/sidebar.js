/**
 * Controle da sidebar: collapse/expand (desktop) e drawer (mobile)
 */
(function () {
    'use strict';

    const sidebar = document.getElementById('sidebar');
    const overlay = document.getElementById('sidebar-overlay');
    const btnToggleDesktop = document.getElementById('sidebar-toggle-desktop');
    const btnToggleMobile = document.getElementById('sidebar-toggle-mobile');
    const STORAGE_KEY = 'sidebar-collapsed';

    if (!sidebar) return;

    // Desktop: collapse/expand
    function toggleDesktop() {
        sidebar.classList.toggle('collapsed');
        const isCollapsed = sidebar.classList.contains('collapsed');
        localStorage.setItem(STORAGE_KEY, isCollapsed ? '1' : '0');
    }

    // Mobile: drawer open/close
    function openMobile() {
        sidebar.classList.add('open');
        if (overlay) overlay.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    function closeMobile() {
        sidebar.classList.remove('open');
        if (overlay) overlay.style.display = 'none';
        document.body.style.overflow = '';
    }

    // Restaurar estado desktop
    if (window.innerWidth > 768 && localStorage.getItem(STORAGE_KEY) === '1') {
        sidebar.classList.add('collapsed');
    }

    if (btnToggleDesktop) btnToggleDesktop.addEventListener('click', toggleDesktop);
    if (btnToggleMobile) btnToggleMobile.addEventListener('click', openMobile);
    if (overlay) overlay.addEventListener('click', closeMobile);

    // Fechar sidebar mobile com Escape
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && sidebar.classList.contains('open')) {
            closeMobile();
        }
    });
})();
