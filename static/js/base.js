// Navbar scroll effect
window.addEventListener('scroll', function() {
    const navbar = document.getElementById('mainNavbar');
    const backToTop = document.getElementById('backToTop');
    
    if (window.scrollY > 100) {
        navbar.classList.add('scrolled');
        backToTop.style.display = 'block';
    } else {
        navbar.classList.remove('scrolled');
        backToTop.style.display = 'none';
    }
});

// Smooth scroll to section
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        const navbarHeight = document.querySelector('.navbar').offsetHeight;
        const elementPosition = element.offsetTop - navbarHeight;
        
        window.scrollTo({
            top: elementPosition,
            behavior: 'smooth'
        });
    }
}

// Scroll to top
function scrollToTop() {
    window.scrollTo({
        top: 0,
        behavior: 'smooth'
    });
}

// Intersection Observer for animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Initialize animations and interactions
document.addEventListener('DOMContentLoaded', function() {
    const cards = document.querySelectorAll('.service-card, .news-card');
    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });

    // Add click handlers for service cards
    const serviceCards = document.querySelectorAll('.service-card');
    serviceCards.forEach(card => {
        card.addEventListener('click', function() {
            // Add ripple effect
            const ripple = document.createElement('div');
            ripple.style.position = 'absolute';
            ripple.style.borderRadius = '50%';
            ripple.style.background = 'rgba(0, 38, 62, 0.6)';
            ripple.style.transform = 'scale(0)';
            ripple.style.animation = 'ripple 0.6s linear';
            ripple.style.left = '50%';
            ripple.style.top = '50%';
            ripple.style.width = '20px';
            ripple.style.height = '20px';
            ripple.style.marginLeft = '-10px';
            ripple.style.marginTop = '-10px';
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Add CSS for ripple animation
    const style = document.createElement('style');
    style.textContent = `
        @keyframes ripple {
            to {
                transform: scale(4);
                opacity: 0;
            }
        }
    `;
    document.head.appendChild(style);

    // Mobile menu improvements
    const navbarToggler = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (navbarToggler && navbarCollapse) {
        navbarToggler.addEventListener('click', function() {
            setTimeout(() => {
                if (navbarCollapse.classList.contains('show')) {
                    document.body.style.overflow = 'hidden';
                } else {
                    document.body.style.overflow = 'auto';
                }
            }, 300);
        });
    }

    // Modified: Only close mobile menu when clicking on non-dropdown links
    const navLinks = document.querySelectorAll('.nav-link');
    navLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            // Prevent scrolling to footer for contact link 
            if (this.getAttribute('href') === '#' || this.getAttribute('data-bs-toggle') === 'dropdown') {
                event.preventDefault();
            }
            
            if (window.innerWidth < 992) {
                // Don't close menu if this is a dropdown toggle
                if (this.classList.contains('dropdown-toggle')) {
                    // Prevent default to handle dropdown manually
                    event.preventDefault();
                    
                    // Toggle dropdown menu visibility
                    const dropdownMenu = this.nextElementSibling;
                    if (dropdownMenu && dropdownMenu.classList.contains('dropdown-menu')) {
                        if (dropdownMenu.style.display === 'block') {
                            dropdownMenu.style.display = '';
                        } else {
                            dropdownMenu.style.display = 'block';
                        }
                    }
                } else {
                    // This is a regular link, close the mobile menu
                    const navbarCollapse = document.querySelector('.navbar-collapse');
                    if (navbarCollapse.classList.contains('show')) {
                        navbarToggler.click();
                    }
                }
            }
        });
    });
});

// Parallax effect for hero section
window.addEventListener('scroll', function() {
    const heroSection = document.querySelector('.hero-section');
    const scrolled = window.pageYOffset;
    const rate = scrolled * -0.5;
    
    if (heroSection) {
        heroSection.style.backgroundPosition = `center ${rate}px`;
    }
});

// Add loading animation
window.addEventListener('load', function() {
    document.body.classList.add('loaded');
    
    // Animate hero content
    const heroContent = document.querySelector('.hero-content');
    if (heroContent) {
        heroContent.style.opacity = '1';
        heroContent.style.transform = 'translateY(0)';
    }
});