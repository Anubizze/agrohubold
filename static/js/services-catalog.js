(function () {
    'use strict';

    var drawer = document.getElementById('catDrawer');
    var backdrop = document.getElementById('catDrawerBackdrop');
    if (!drawer) {
        return;
    }

    var closeBtn = document.getElementById('catDrawerClose');
    var bookBtn = document.getElementById('drawerBook');
    var consultBtn = document.getElementById('drawerConsult');
    var currentItem = null;

    function openDrawer(item) {
        currentItem = item;
        document.getElementById('drawerTitle').textContent = item.getAttribute('data-name') || '';
        document.getElementById('drawerDesc').textContent = item.getAttribute('data-desc') || '';
        document.getElementById('drawerDuration').textContent = item.getAttribute('data-duration') || '';
        document.getElementById('drawerPrice').textContent = item.getAttribute('data-price') || '';
        document.getElementById('drawerResult').textContent = item.getAttribute('data-result') || item.getAttribute('data-desc') || '';

        var prepEl = document.getElementById('drawerPrep');
        prepEl.innerHTML = '';
        var prep = (item.getAttribute('data-prep') || '')
            .split('|')
            .map(function (s) { return s.trim(); })
            .filter(Boolean);
        if (!prep.length) {
            prep = ['Следуйте инструкции лаборатории'];
        }
        prep.forEach(function (line) {
            var li = document.createElement('li');
            li.textContent = line;
            prepEl.appendChild(li);
        });

        backdrop.hidden = false;
        drawer.classList.add('is-open');
        drawer.setAttribute('aria-hidden', 'false');
        document.body.classList.add('drawer-open');
    }

    function closeDrawer() {
        drawer.classList.remove('is-open');
        drawer.setAttribute('aria-hidden', 'true');
        backdrop.hidden = true;
        document.body.classList.remove('drawer-open');
        currentItem = null;
    }

    function isDemoId(id) {
        return !id || id === '0' || String(id).indexOf('demo') === 0;
    }

    function handleCart(item) {
        if (!item) return;
        var id = item.getAttribute('data-id') || '';
        var name = item.getAttribute('data-name') || '';
        if (isDemoId(id)) {
            if (typeof openConsultationModal === 'function') {
                openConsultationModal(0, name);
            }
            return;
        }
        if (typeof addToCart === 'function') {
            addToCart(Number(id), name);
        }
    }

    document.addEventListener('click', function (e) {
        var more = e.target.closest('[data-open-drawer]');
        if (more) {
            var item = more.closest('.cat-item');
            if (item) openDrawer(item);
            return;
        }

        var cart = e.target.closest('.cat-item__cart');
        if (cart) {
            handleCart(cart.closest('.cat-item'));
        }
    });

    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);
    if (backdrop) backdrop.addEventListener('click', closeDrawer);
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') closeDrawer();
    });

    if (bookBtn) {
        bookBtn.addEventListener('click', function () {
            if (!currentItem) return;
            var item = currentItem;
            closeDrawer();
            handleCart(item);
        });
    }

    if (consultBtn) {
        consultBtn.addEventListener('click', function () {
            if (!currentItem) return;
            var id = currentItem.getAttribute('data-id') || '';
            var name = currentItem.getAttribute('data-name') || '';
            closeDrawer();
            if (typeof openConsultationModal === 'function') {
                openConsultationModal(isDemoId(id) ? 0 : Number(id), name);
            }
        });
    }

    var filters = document.getElementById('catFilters');
    var activeFilter = 'all';

    function visibleItems() {
        return document.querySelectorAll('#catList .cat-item');
    }

    function applyFilterAndSearch() {
        var q = ((document.getElementById('catSearchInput') || {}).value || '').trim().toLowerCase();
        visibleItems().forEach(function (item) {
            var f = item.getAttribute('data-filter') || 'all';
            var hay = (item.getAttribute('data-search') || item.textContent || '').toLowerCase();
            var okFilter = activeFilter === 'all' || f === activeFilter || f === 'all';
            var okSearch = !q || hay.indexOf(q) !== -1;
            item.classList.toggle('is-hidden', !(okFilter && okSearch));
        });
    }

    if (filters && !filters.hidden) {
        filters.addEventListener('click', function (e) {
            var btn = e.target.closest('.cat-filter');
            if (!btn) return;
            filters.querySelectorAll('.cat-filter').forEach(function (b) { b.classList.remove('is-active'); });
            btn.classList.add('is-active');
            activeFilter = btn.getAttribute('data-filter') || 'all';
            applyFilterAndSearch();
        });
    }

    var searchInput = document.getElementById('catSearchInput');
    var searchBtn = document.getElementById('catSearchBtn');
    if (searchInput) searchInput.addEventListener('input', applyFilterAndSearch);
    if (searchBtn) searchBtn.addEventListener('click', applyFilterAndSearch);

    var anchors = document.querySelectorAll('#catAnchors a');
    var sections = ['cat-services', 'cat-categories', 'cat-analyses', 'site-contacts']
        .map(function (id) { return document.getElementById(id); })
        .filter(Boolean);

    function setActiveAnchor() {
        var current = sections[0] && sections[0].id;
        var offset = 160;
        sections.forEach(function (sec) {
            if (sec.getBoundingClientRect().top - offset <= 0) current = sec.id;
        });
        anchors.forEach(function (a) {
            a.classList.toggle('is-active', a.getAttribute('href') === '#' + current);
        });
    }

    anchors.forEach(function (a) {
        a.addEventListener('click', function (e) {
            var href = a.getAttribute('href');
            if (!href || href.charAt(0) !== '#') return;
            var target = document.querySelector(href);
            if (!target) return;
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        });
    });

    window.addEventListener('scroll', setActiveAnchor, { passive: true });
    setActiveAnchor();
})();
