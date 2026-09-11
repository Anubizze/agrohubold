(function () {
    'use strict';

    var buttons = document.querySelectorAll('.pd-tabs__btn[data-pd-tab]');
    var panels = document.querySelectorAll('.pd-tab-panel[data-pd-panel]');
    if (buttons.length && panels.length) {
        buttons.forEach(function (button) {
            button.addEventListener('click', function () {
                var target = button.getAttribute('data-pd-tab');
                buttons.forEach(function (btn) {
                    var active = btn === button;
                    btn.classList.toggle('is-active', active);
                    btn.setAttribute('aria-selected', active ? 'true' : 'false');
                });
                panels.forEach(function (panel) {
                    var show = panel.getAttribute('data-pd-panel') === target;
                    panel.classList.toggle('is-active', show);
                    panel.hidden = !show;
                });
            });
        });
    }

    var tablesRoot = document.getElementById('pdTables');
    if (!tablesRoot) return;

    var isAccordion = tablesRoot.classList.contains('pd-tables--accordion');
    tablesRoot.querySelectorAll('details.pd-table').forEach(function (item) {
        if (!isAccordion) {
            item.open = true;
            item.addEventListener('toggle', function () {
                if (!item.open) item.open = true;
            });
            return;
        }
        item.addEventListener('toggle', function () {
            if (item.getAttribute('data-keep-open') === '1' && !item.open) {
                item.open = true;
            }
        });
    });
})();
