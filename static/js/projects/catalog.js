document.addEventListener('DOMContentLoaded', function () {
    var cards = document.querySelectorAll('.offers-card');
    if (cards.length) {
        var observer = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.12 });

        cards.forEach(function (card, i) {
            card.style.opacity = '0';
            card.style.transform = 'translateY(14px)';
            card.style.transition = 'opacity 0.4s ease ' + (i % 6) * 0.05 + 's, transform 0.4s ease ' + (i % 6) * 0.05 + 's';
            observer.observe(card);
        });

        var style = document.createElement('style');
        style.textContent = '.offers-card.is-visible { opacity: 1 !important; transform: none !important; }';
        document.head.appendChild(style);
    }

    var drawer = document.getElementById('ipDrawer');
    var backdrop = document.getElementById('ipDrawerBackdrop');
    if (!drawer || !backdrop) return;

    var closeBtn = document.getElementById('ipDrawerClose');
    var downloadBtn = document.getElementById('ipDrawerDownload');
    var applyBtn = document.getElementById('ipDrawerApply');

    function openDrawer(item) {
        document.getElementById('ipDrawerTitle').textContent = item.getAttribute('data-name') || '';
        document.getElementById('ipDrawerType').textContent = item.getAttribute('data-type') || '';
        document.getElementById('ipDrawerNumber').textContent = item.getAttribute('data-number') || '—';
        document.getElementById('ipDrawerDate').textContent = item.getAttribute('data-date') || '—';
        document.getElementById('ipDrawerDesc').textContent = item.getAttribute('data-desc') || '';

        var list = document.getElementById('ipDrawerBenefits');
        list.innerHTML = '';
        var benefits = (item.getAttribute('data-benefits') || '')
            .split(/\r?\n|\|/)
            .map(function (s) { return s.trim(); })
            .filter(Boolean);
        if (!benefits.length) {
            benefits = [item.getAttribute('data-desc') || ''].filter(Boolean);
        }
        benefits.forEach(function (line) {
            var li = document.createElement('li');
            li.textContent = line;
            list.appendChild(li);
        });

        var doc = item.getAttribute('data-doc') || '';
        if (doc) {
            downloadBtn.href = doc;
            downloadBtn.hidden = false;
        } else {
            downloadBtn.removeAttribute('href');
            downloadBtn.hidden = true;
        }

        if (applyBtn) {
            var title = encodeURIComponent(item.getAttribute('data-name') || '');
            applyBtn.href = 'https://wa.me/+77476219861?text=' + title;
        }

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
    }

    document.addEventListener('click', function (e) {
        var btn = e.target.closest('[data-open-ip-drawer]');
        if (btn) {
            var item = btn.closest('.ip-card');
            if (item) openDrawer(item);
            return;
        }
        if (e.target === backdrop) closeDrawer();
    });

    if (closeBtn) closeBtn.addEventListener('click', closeDrawer);

    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && drawer.classList.contains('is-open')) {
            closeDrawer();
        }
    });
});
