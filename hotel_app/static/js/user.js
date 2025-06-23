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

    const progressBars = document.querySelectorAll('.progress-fill');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });

    
});

let selectedRating = 0;

// Modal Functions
function openReservationModal() {
    document.getElementById('reservationModal').classList.remove('hidden');
    resetRating();
}

function closeReservationModal() {
    document.getElementById('reservationModal').classList.add('hidden');
    resetRating();
}

function closeRatingCompletedModal() {
    document.getElementById('ratingCompletedModal').classList.add('hidden');
    stopConfetti();
}

// Rating Functions
function selectRating(rating) {
    selectedRating = rating;
    updateStarDisplay();
    updateRatingText(rating);
    enableSubmitButton();
}

function updateStarDisplay() {
    const stars = document.querySelectorAll('.rating-star');
    stars.forEach((star, index) => {
        if (index < selectedRating) {
            star.classList.add('active');
        } else {
            star.classList.remove('active');
        }
    });
}

function updateRatingText(rating) {
    const ratingTexts = {
        1: "Poor - We're sorry to hear that",
        2: "Fair - We'll work to improve",
        3: "Good - Thanks for your feedback",
        4: "Very Good - We're glad you enjoyed it",
        5: "Excellent - Thank you for the amazing review!"
    };

    document.getElementById('ratingText').textContent = ratingTexts[rating] || '';
}

function enableSubmitButton() {
    const submitBtn = document.getElementById('submitRatingBtn');
    if (selectedRating > 0) {
        submitBtn.disabled = false;
        submitBtn.classList.remove('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
        submitBtn.classList.add('bg-purple-600', 'hover:bg-purple-700', 'text-white', 'cursor-pointer');
    } else {
        submitBtn.disabled = true;
        submitBtn.classList.add('bg-gray-300', 'text-gray-500', 'cursor-not-allowed');
        submitBtn.classList.remove('bg-purple-600', 'hover:bg-purple-700', 'text-white', 'cursor-pointer');
    }
}

function resetRating() {
    selectedRating = 0;
    updateStarDisplay();
    document.getElementById('ratingText').textContent = '';
    document.getElementById('ratingComment').value = '';
    enableSubmitButton();
}

function submitRating() {
    if (selectedRating === 0) return;

    // Hide the rating modal
    closeReservationModal();

    // Show the completion modal
    document.getElementById('ratingCompletedModal').classList.remove('hidden');

    // Start confetti animation
    startConfetti();

    // Auto-close the completion modal after 3 seconds
    setTimeout(() => {
        closeRatingCompletedModal();
    }, 3000);
}

// Confetti Functions
function startConfetti() {
    const container = document.getElementById('confetti-container');
    container.style.display = 'block';
    container.innerHTML = '';

    // Create confetti pieces
    for (let i = 0; i < 50; i++) {
        createConfettiPiece(container);
    }

    // Stop confetti after 4 seconds
    setTimeout(() => {
        stopConfetti();
    }, 4000);
}

function createConfettiPiece(container) {
    const confetti = document.createElement('div');
    confetti.className = 'confetti';

    // Random shapes
    const shapes = ['square', 'circle', 'triangle'];
    const randomShape = shapes[Math.floor(Math.random() * shapes.length)];
    confetti.classList.add(randomShape);

    // Random colors
    const colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#fd79a8', '#fdcb6e', '#6c5ce7', '#a29bfe', '#00b894'];
    const randomColor = colors[Math.floor(Math.random() * colors.length)];

    if (randomShape !== 'triangle') {
        confetti.style.backgroundColor = randomColor;
    }

    // Random position and animation
    confetti.style.left = Math.random() * 100 + '%';
    confetti.style.animationDelay = Math.random() * 2 + 's';
    confetti.style.animationDuration = (Math.random() * 2 + 2) + 's';

    container.appendChild(confetti);
}

function stopConfetti() {
    const container = document.getElementById('confetti-container');
    container.style.display = 'none';
    container.innerHTML = '';
}

function openRulesModal() {
    document.getElementById('rulesModal').classList.remove('hidden');
}

function closeRulesModal() {
    document.getElementById('rulesModal').classList.add('hidden');
}

let currentTab = 'all';

function switchTab(tab) {
    currentTab = tab;

    // Update tab buttons
    document.querySelectorAll('[id^="tab-"]').forEach(btn => {
        btn.classList.remove('bg-white', 'text-purple-600', 'shadow-sm');
        btn.classList.add('text-gray-600', 'hover:text-gray-900');
    });

    document.getElementById(`tab-${tab}`).classList.add('bg-white', 'text-purple-600', 'shadow-sm');
    document.getElementById(`tab-${tab}`).classList.remove('text-gray-600', 'hover:text-gray-900');

    // Filter cards
    const allCards = document.querySelectorAll('.order-card');
    allCards.forEach(card => {
        if (tab === 'all' || card.classList.contains(tab)) {
            card.classList.remove('hidden');
        } else {
            card.classList.add('hidden');
        }
    });
}

function viewOrderDetails(orderId) {
    alert(`Viewing details for order: ${orderId}`);
}

function rateOrder(orderId) {
    alert(`Opening rating modal for order: ${orderId}`);
    // Here you would open the rating modal
}

function closeOrderModal() {
    document.getElementById('orderModal').classList.add('hidden');
}

function openOrderModal() {
    document.getElementById('orderModal').classList.remove('hidden');
}

function makeReservation(event) {
    event.preventDefault();
    alert('Searching for available hotels...');
    closeReservationModal();
}

function viewReservations() {
    openOrderModal();
}

function viewAnalytics() {
    alert('Opening analytics dashboard...');
}

function contactSupport() {
    alert('Opening customer support...');
}

// Close modals when clicking outside
document.addEventListener('click', function (event) {
    const modals = ['reservationModal', 'rulesModal', 'orderModal'];
    modals.forEach(modalId => {
        const modal = document.getElementById(modalId);
        if (event.target === modal) {
            modal.classList.add('hidden');
        }
    });
});

// Set minimum date to today for date inputs
document.addEventListener('DOMContentLoaded', function () {
    const today = new Date().toISOString().split('T')[0];
    const dateInputs = document.querySelectorAll('input[type="date"]');
    dateInputs.forEach(input => {
        input.min = today;
    });
});

function navigateToPage(pageName) {
    // Check if it's an external link or internal page
    if (pageName.startsWith('http')) {
        // External link - open in new tab
        window.open(pageName, '_blank');
    } else {
        // Internal page - navigate in same window
        window.location.href = pageName;
    }
}

function logout() {
    if (confirm('Are you sure you want to sign out?')) {
        // Add logout logic here
        console.log('Logging out...');
        // Example: window.location.href = '/login';
    }
}

// Add smooth scroll behavior
document.documentElement.style.scrollBehavior = 'smooth';