// Smooth scroll for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Navbar scroll effect
let lastScroll = 0;
const navbar = document.querySelector('.navbar');

window.addEventListener('scroll', () => {
    const currentScroll = window.pageYOffset;

    if (currentScroll <= 0) {
        navbar.style.boxShadow = 'none';
    } else {
        navbar.style.boxShadow = '0 4px 20px rgba(0, 0, 0, 0.3)';
    }

    lastScroll = currentScroll;
});

// Intersection Observer for fade-in animations
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -100px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe feature cards, pricing cards, and stat items
const animatedElements = document.querySelectorAll('.feature-card, .pricing-card, .stat-item');
animatedElements.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(30px)';
    el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(el);
});

// Counter animation for stats
const animateCounter = (element, target, duration = 2000) => {
    const start = 0;
    const increment = target / (duration / 16);
    let current = start;

    const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
            current = target;
            clearInterval(timer);
        }

        // Format number with commas
        const formatted = Math.floor(current).toLocaleString();
        element.textContent = element.textContent.replace(/[\d,]+/, formatted);
    }, 16);
};

// Observe stats section for counter animation
const statsObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const statNumbers = entry.target.querySelectorAll('.stat-number');
            statNumbers.forEach(stat => {
                const text = stat.textContent;
                const number = parseInt(text.replace(/\D/g, ''));
                if (number) {
                    animateCounter(stat, number);
                }
            });
            statsObserver.unobserve(entry.target);
        }
    });
}, { threshold: 0.3 });

const statsSection = document.querySelector('.stats');
if (statsSection) {
    statsObserver.observe(statsSection);
}

// Mobile menu toggle (if needed)
const createMobileMenu = () => {
    const navLinks = document.querySelector('.nav-links');
    const navCta = document.querySelector('.nav-cta');

    if (window.innerWidth <= 1024) {
        const menuButton = document.createElement('button');
        menuButton.className = 'mobile-menu-button';
        menuButton.innerHTML = `
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M3 12h18M3 6h18M3 18h18" stroke-width="2" stroke-linecap="round"/>
            </svg>
        `;

        menuButton.addEventListener('click', () => {
            navLinks.classList.toggle('active');
            navCta.classList.toggle('active');
        });

        const logo = document.querySelector('.logo');
        logo.parentNode.insertBefore(menuButton, logo.nextSibling);
    }
};

// Parallax effect for hero background
window.addEventListener('scroll', () => {
    const scrolled = window.pageYOffset;
    const heroBackground = document.querySelector('.hero-background');
    if (heroBackground && scrolled < window.innerHeight) {
        heroBackground.style.transform = `translateY(${scrolled * 0.5}px)`;
    }
});

// Add loading animation
window.addEventListener('load', () => {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease';
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
});

// Download button tracking (placeholder for analytics)
const downloadButtons = document.querySelectorAll('.download-btn, .btn-primary');
downloadButtons.forEach(button => {
    button.addEventListener('click', (e) => {
        const buttonText = button.textContent.trim();
        console.log('Download button clicked:', buttonText);
        // Add analytics tracking here
        // e.g., gtag('event', 'download_click', { button: buttonText });
    });
});

// Add hover effect to phone mockup
const phoneMockup = document.querySelector('.phone-mockup');
if (phoneMockup) {
    phoneMockup.addEventListener('mousemove', (e) => {
        const rect = phoneMockup.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = (y - centerY) / 20;
        const rotateY = (centerX - x) / 20;

        phoneMockup.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
    });

    phoneMockup.addEventListener('mouseleave', () => {
        phoneMockup.style.transform = '';
    });
}

// Dynamic year in footer
const currentYear = new Date().getFullYear();
const footerText = document.querySelector('.footer-bottom p');
if (footerText) {
    footerText.textContent = footerText.textContent.replace('2025', currentYear);
}

// Form validation (if contact form is added)
const validateEmail = (email) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
};

// Lazy loading for images (if added)
if ('IntersectionObserver' in window) {
    const imageObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                if (img.dataset.src) {
                    img.src = img.dataset.src;
                    img.classList.add('loaded');
                    imageObserver.unobserve(img);
                }
            }
        });
    });

    document.querySelectorAll('img[data-src]').forEach(img => {
        imageObserver.observe(img);
    });
}

// FAQ Toggle Functionality
const initFAQ = () => {
    const faqItems = document.querySelectorAll('.faq-item');

    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');

        question.addEventListener('click', () => {
            const isActive = item.classList.contains('active');

            // Close all other FAQ items
            faqItems.forEach(otherItem => {
                if (otherItem !== item) {
                    otherItem.classList.remove('active');
                }
            });

            // Toggle current item
            if (isActive) {
                item.classList.remove('active');
            } else {
                item.classList.add('active');
            }
        });
    });
};

// Screenshot hover effect
const initScreenshotEffects = () => {
    const screenshots = document.querySelectorAll('.screenshot-frame');

    screenshots.forEach(frame => {
        frame.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-10px) scale(1.02)';
        });

        frame.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
    });
};

// Carousel Functionality
const initCarousel = () => {
    const track = document.querySelector('.carousel-track');
    const slides = Array.from(document.querySelectorAll('.carousel-slide'));
    const prevBtn = document.querySelector('.carousel-prev');
    const nextBtn = document.querySelector('.carousel-next');
    const dotsContainer = document.querySelector('.carousel-dots');

    if (!track || slides.length === 0) return;

    let currentIndex = 0;
    let slidesToShow = 3;
    let autoplayInterval;
    const autoplayDelay = 5000;

    // Determine slides to show based on screen width
    const updateSlidesToShow = () => {
        if (window.innerWidth <= 768) {
            slidesToShow = 1;
        } else if (window.innerWidth <= 1024) {
            slidesToShow = 2;
        } else {
            slidesToShow = 3;
        }
    };

    // Create dots
    const createDots = () => {
        dotsContainer.innerHTML = '';
        const totalDots = Math.ceil(slides.length - slidesToShow + 1);

        for (let i = 0; i < totalDots; i++) {
            const dot = document.createElement('button');
            dot.classList.add('carousel-dot');
            dot.setAttribute('aria-label', `Go to slide ${i + 1}`);
            if (i === 0) dot.classList.add('active');

            dot.addEventListener('click', () => {
                currentIndex = i;
                updateCarousel();
                resetAutoplay();
            });

            dotsContainer.appendChild(dot);
        }
    };

    // Update carousel position
    const updateCarousel = () => {
        const slideWidth = slides[0].offsetWidth;
        const gap = 32; // 2rem in pixels
        const offset = -(currentIndex * (slideWidth + gap));

        track.style.transform = `translateX(${offset}px)`;

        // Update dots
        const dots = document.querySelectorAll('.carousel-dot');
        dots.forEach((dot, index) => {
            dot.classList.toggle('active', index === currentIndex);
        });

        // Update button states
        prevBtn.disabled = currentIndex === 0;
        nextBtn.disabled = currentIndex >= slides.length - slidesToShow;

        prevBtn.style.opacity = currentIndex === 0 ? '0.5' : '1';
        nextBtn.style.opacity = currentIndex >= slides.length - slidesToShow ? '0.5' : '1';
    };

    // Navigate to previous slide
    const goToPrev = () => {
        if (currentIndex > 0) {
            currentIndex--;
            updateCarousel();
            resetAutoplay();
        }
    };

    // Navigate to next slide
    const goToNext = () => {
        if (currentIndex < slides.length - slidesToShow) {
            currentIndex++;
            updateCarousel();
            resetAutoplay();
        }
    };

    // Autoplay functionality
    const startAutoplay = () => {
        autoplayInterval = setInterval(() => {
            if (currentIndex >= slides.length - slidesToShow) {
                currentIndex = 0;
            } else {
                currentIndex++;
            }
            updateCarousel();
        }, autoplayDelay);
    };

    const stopAutoplay = () => {
        if (autoplayInterval) {
            clearInterval(autoplayInterval);
        }
    };

    const resetAutoplay = () => {
        stopAutoplay();
        startAutoplay();
    };

    // Touch/Swipe support
    let touchStartX = 0;
    let touchEndX = 0;

    track.addEventListener('touchstart', (e) => {
        touchStartX = e.changedTouches[0].screenX;
        stopAutoplay();
    });

    track.addEventListener('touchend', (e) => {
        touchEndX = e.changedTouches[0].screenX;
        handleSwipe();
        resetAutoplay();
    });

    const handleSwipe = () => {
        const swipeThreshold = 50;
        const diff = touchStartX - touchEndX;

        if (Math.abs(diff) > swipeThreshold) {
            if (diff > 0) {
                goToNext();
            } else {
                goToPrev();
            }
        }
    };

    // Mouse drag support
    let isDragging = false;
    let startPos = 0;
    let currentTranslate = 0;
    let prevTranslate = 0;

    track.addEventListener('mousedown', (e) => {
        isDragging = true;
        startPos = e.pageX;
        track.style.cursor = 'grabbing';
        stopAutoplay();
    });

    track.addEventListener('mousemove', (e) => {
        if (!isDragging) return;
        const currentPosition = e.pageX;
        currentTranslate = prevTranslate + currentPosition - startPos;
    });

    track.addEventListener('mouseup', () => {
        isDragging = false;
        track.style.cursor = 'grab';

        const movedBy = currentTranslate - prevTranslate;
        const threshold = 100;

        if (movedBy < -threshold && currentIndex < slides.length - slidesToShow) {
            currentIndex++;
        } else if (movedBy > threshold && currentIndex > 0) {
            currentIndex--;
        }

        updateCarousel();
        prevTranslate = currentTranslate;
        resetAutoplay();
    });

    track.addEventListener('mouseleave', () => {
        if (isDragging) {
            isDragging = false;
            track.style.cursor = 'grab';
            updateCarousel();
            resetAutoplay();
        }
    });

    // Event listeners
    prevBtn.addEventListener('click', goToPrev);
    nextBtn.addEventListener('click', goToNext);

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') goToPrev();
        if (e.key === 'ArrowRight') goToNext();
    });

    // Initialize and handle resize
    updateSlidesToShow();
    createDots();
    updateCarousel();
    startAutoplay();

    window.addEventListener('resize', () => {
        const oldSlidesToShow = slidesToShow;
        updateSlidesToShow();

        if (oldSlidesToShow !== slidesToShow) {
            currentIndex = 0;
            createDots();
            updateCarousel();
        }
    });

    // Pause autoplay on hover
    const carouselContainer = document.querySelector('.carousel-container');
    carouselContainer.addEventListener('mouseenter', stopAutoplay);
    carouselContainer.addEventListener('mouseleave', startAutoplay);
};

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    console.log('Fenzy Landing Page Loaded');

    // Initialize translation system
    if (typeof initTranslation === 'function') {
        await initTranslation();
    }

    createMobileMenu();
    initFAQ();
    initScreenshotEffects();
    initCarousel();
});
