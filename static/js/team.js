document.addEventListener('DOMContentLoaded', function () {
    var cards = document.querySelectorAll('.tm-card');
    if (!cards.length) return;

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
        card.style.transform = 'translateY(16px)';
        card.style.transition = 'opacity 0.45s ease ' + (i % 8) * 0.05 + 's, transform 0.45s ease ' + (i % 8) * 0.05 + 's';
        observer.observe(card);
    });

    var style = document.createElement('style');
    style.textContent = '.tm-card.is-visible { opacity: 1 !important; transform: none !important; }';
    document.head.appendChild(style);
});
