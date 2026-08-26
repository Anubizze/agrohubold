document.addEventListener('DOMContentLoaded', function () {
    var searchInput = document.getElementById('crsSearchInput');
    var searchBtn = document.getElementById('crsSearchBtn');
    var formatBar = document.getElementById('crsFormats');
    var cards = document.querySelectorAll('#crsGrid .crs-card');
    var dirs = document.querySelectorAll('#crsDirections .crs-dir-card');
    var activeFormat = 'all';

    function applyFilters() {
        var q = (searchInput && searchInput.value ? searchInput.value : '').trim().toLowerCase();

        cards.forEach(function (card) {
            var hay = (card.getAttribute('data-search') || '').toLowerCase();
            var format = card.getAttribute('data-format') || 'all';
            var okSearch = !q || hay.indexOf(q) !== -1;
            var okFormat = activeFormat === 'all' || format === activeFormat;
            card.classList.toggle('is-hidden', !(okSearch && okFormat));
        });

        dirs.forEach(function (card) {
            var hay = (card.getAttribute('data-search') || '').toLowerCase();
            card.classList.toggle('is-hidden', !(!q || hay.indexOf(q) !== -1));
        });
    }

    if (searchInput) searchInput.addEventListener('input', applyFilters);
    if (searchBtn) searchBtn.addEventListener('click', applyFilters);

    if (formatBar) {
        formatBar.addEventListener('click', function (e) {
            var btn = e.target.closest('[data-format]');
            if (!btn) return;
            formatBar.querySelectorAll('[data-format]').forEach(function (b) {
                b.classList.remove('is-active');
            });
            btn.classList.add('is-active');
            activeFormat = btn.getAttribute('data-format') || 'all';
            applyFilters();
        });
    }

    var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
            if (entry.isIntersecting) {
                entry.target.classList.add('is-visible');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.12 });

    document.querySelectorAll('.crs-card, .crs-dir-card').forEach(function (el, i) {
        el.style.opacity = '0';
        el.style.transform = 'translateY(16px)';
        el.style.transition = 'opacity 0.4s ease ' + (i % 6) * 0.05 + 's, transform 0.4s ease ' + (i % 6) * 0.05 + 's';
        observer.observe(el);
    });

    var style = document.createElement('style');
    style.textContent = '.crs-card.is-visible, .crs-dir-card.is-visible { opacity: 1 !important; transform: none !important; }';
    document.head.appendChild(style);
});
