(function () {
    'use strict';

    var buttons = document.querySelectorAll('.pd-tabs__btn[data-pd-tab]');
    var panels = document.querySelectorAll('.pd-tab-panel[data-pd-panel]');
    if (!buttons.length || !panels.length) return;

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
})();
