document.addEventListener('DOMContentLoaded', function () {
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const revealItems = document.querySelectorAll('.reveal');
    if (revealItems.length) {
        if (reduceMotion || !('IntersectionObserver' in window)) {
            revealItems.forEach(function (el) {
                el.classList.add('is-visible');
            });
        } else {
            const observer = new IntersectionObserver(
                function (entries) {
                    entries.forEach(function (entry) {
                        if (entry.isIntersecting) {
                            entry.target.classList.add('is-visible');
                            observer.unobserve(entry.target);
                        }
                    });
                },
                { threshold: 0.14, rootMargin: '0px 0px -40px 0px' }
            );

            revealItems.forEach(function (el) {
                observer.observe(el);
            });
        }
    }

    const newsCards = document.querySelectorAll('.home-news-card');
    newsCards.forEach(function (card) {
        card.addEventListener('click', function () {
            card.style.transform = 'scale(0.99)';
            window.setTimeout(function () {
                card.style.transform = '';
            }, 140);
        });
    });

    initServicesSlider();
});

function initServicesSlider() {
    const track = document.getElementById('servicesTrack');
    const prevBtn = document.getElementById('servicesPrev');
    const nextBtn = document.getElementById('servicesNext');
    const dotsWrap = document.getElementById('servicesDots');

    if (!track || !prevBtn || !nextBtn) {
        return;
    }

    const slides = Array.prototype.slice.call(track.querySelectorAll('.home-service'));
    if (!slides.length) {
        return;
    }

    let page = 0;
    let perView = getPerView();
    let pageCount = Math.ceil(slides.length / perView);

    function getPerView() {
        const width = window.innerWidth;
        if (width < 640) return 1;
        if (width < 900) return 2;
        return 3;
    }

    function buildDots() {
        if (!dotsWrap) return;
        dotsWrap.innerHTML = '';
        for (let i = 0; i < pageCount; i += 1) {
            const dot = document.createElement('button');
            dot.type = 'button';
            dot.className = 'home-slider__dot' + (i === page ? ' is-active' : '');
            dot.setAttribute('aria-label', 'Slide ' + (i + 1));
            dot.addEventListener('click', function () {
                page = i;
                update();
            });
            dotsWrap.appendChild(dot);
        }
    }

    function update() {
        perView = getPerView();
        pageCount = Math.ceil(slides.length / perView);
        if (page > pageCount - 1) page = pageCount - 1;
        if (page < 0) page = 0;

        const gap = parseFloat(window.getComputedStyle(track).gap) || 0;
        const slideWidth = slides[0].getBoundingClientRect().width;
        const offset = page * perView * (slideWidth + gap);
        track.style.transform = 'translate3d(' + (-offset) + 'px, 0, 0)';

        prevBtn.disabled = page <= 0;
        nextBtn.disabled = page >= pageCount - 1;

        if (dotsWrap) {
            const dots = dotsWrap.querySelectorAll('.home-slider__dot');
            if (dots.length !== pageCount) {
                buildDots();
            } else {
                dots.forEach(function (dot, i) {
                    dot.classList.toggle('is-active', i === page);
                });
            }
        }
    }

    prevBtn.addEventListener('click', function () {
        page = Math.max(0, page - 1);
        update();
    });

    nextBtn.addEventListener('click', function () {
        page = Math.min(pageCount - 1, page + 1);
        update();
    });

    let touchStartX = 0;
    let touchDeltaX = 0;

    track.addEventListener('touchstart', function (e) {
        touchStartX = e.changedTouches[0].clientX;
        touchDeltaX = 0;
    }, { passive: true });

    track.addEventListener('touchmove', function (e) {
        touchDeltaX = e.changedTouches[0].clientX - touchStartX;
    }, { passive: true });

    track.addEventListener('touchend', function () {
        if (Math.abs(touchDeltaX) < 40) return;
        if (touchDeltaX < 0) {
            page = Math.min(pageCount - 1, page + 1);
        } else {
            page = Math.max(0, page - 1);
        }
        update();
    });

    let resizeTimer;
    window.addEventListener('resize', function () {
        window.clearTimeout(resizeTimer);
        resizeTimer = window.setTimeout(function () {
            buildDots();
            update();
        }, 120);
    });

    buildDots();
    update();
}
