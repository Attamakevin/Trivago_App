// Initialize when DOM is fully loaded
document.addEventListener('DOMContentLoaded', function () {
    let currentSlideIndex = 0;
    let isAutoPlaying = true;
    let autoplayInterval;

    // Select elements after DOM is loaded
    const slides = document.querySelectorAll('.slide');
    const indicators = document.querySelectorAll('.indicator');
    const sliderContainer = document.querySelector('.relative');
    const totalSlides = slides.length;

    console.log('Found', totalSlides, 'slides and', indicators.length, 'indicators');

    if (totalSlides === 0) {
        console.error('No slides found! Check HTML structure.');
        return;
    }

    // Show specific slide
    function showSlide(index) {
        // Ensure index is within bounds
        if (index < 0 || index >= totalSlides) return;

        // Remove active class from all slides and indicators
        slides.forEach(slide => {
            slide.classList.remove('active', 'prev');
        });

        indicators.forEach(indicator => {
            indicator.classList.remove('scale-110');
            indicator.classList.add('bg-opacity-50');
            indicator.classList.remove('bg-white');
        });

        // Add prev class to current slide before switching
        if (slides[currentSlideIndex] && currentSlideIndex !== index) {
            slides[currentSlideIndex].classList.add('prev');
        }

        // Update current index
        currentSlideIndex = index;

        // Show new slide
        if (slides[currentSlideIndex]) {
            slides[currentSlideIndex].classList.add('active');
        }

        if (indicators[currentSlideIndex]) {
            indicators[currentSlideIndex].classList.remove('bg-opacity-50');
            indicators[currentSlideIndex].classList.add('bg-white', 'scale-110');
        }
    }

    // Next slide
    function nextSlide() {
        const nextIndex = (currentSlideIndex + 1) % totalSlides;
        showSlide(nextIndex);
    }

    // Previous slide
    function previousSlide() {
        const prevIndex = (currentSlideIndex - 1 + totalSlides) % totalSlides;
        showSlide(prevIndex);
    }

    // Go to specific slide
    function goToSlide(index) {
        showSlide(index);
        restartAutoplay();
    }

    // Start autoplay
    function startAutoplay() {
        if (isAutoPlaying) {
            autoplayInterval = setInterval(nextSlide, 2000);
        }
    }

    // Stop autoplay
    function stopAutoplay() {
        clearInterval(autoplayInterval);
    }

    // Restart autoplay
    function restartAutoplay() {
        stopAutoplay();
        startAutoplay();
    }

    // Toggle autoplay
    function toggleAutoplay() {
        const playIcon = document.getElementById('playIcon');
        const pauseIcon = document.getElementById('pauseIcon');

        if (isAutoPlaying) {
            stopAutoplay();
            isAutoPlaying = false;
            playIcon.classList.remove('hidden');
            pauseIcon.classList.add('hidden');
        } else {
            isAutoPlaying = true;
            startAutoplay();
            playIcon.classList.add('hidden');
            pauseIcon.classList.remove('hidden');
        }
    }

    // Initialize slider
    function initSlider() {
        console.log('Initializing slider with', totalSlides, 'slides');
        if (totalSlides > 0) {
            showSlide(0);
            startAutoplay();
        }
    }

    // Make functions globally accessible for onclick handlers
    window.nextSlide = nextSlide;
    window.previousSlide = previousSlide;
    window.goToSlide = goToSlide;
    window.toggleAutoplay = toggleAutoplay;

    // Pause on hover (only if slider container exists)
    if (sliderContainer) {
        sliderContainer.addEventListener('mouseenter', stopAutoplay);
        sliderContainer.addEventListener('mouseleave', () => {
            if (isAutoPlaying) startAutoplay();
        });

        // Touch/swipe support for mobile
        let startX = 0;
        let endX = 0;

        sliderContainer.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
        });

        sliderContainer.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            handleSwipe();
        });

        function handleSwipe() {
            const threshold = 50;
            const diff = startX - endX;

            if (Math.abs(diff) > threshold) {
                if (diff > 0) {
                    nextSlide();
                } else {
                    previousSlide();
                }
                restartAutoplay();
            }
        }
    }

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') {
            previousSlide();
            restartAutoplay();
        } else if (e.key === 'ArrowRight') {
            nextSlide();
            restartAutoplay();
        } else if (e.key === ' ') {
            e.preventDefault();
            toggleAutoplay();
        }
    });

    // Initialize slider
    initSlider();
});