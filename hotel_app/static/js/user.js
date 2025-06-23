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

// Reservation Functionality

// Modal Functions
function openReservationModal() {
    document.getElementById('reservationModal').classList.remove('hidden');
}

function closeReservationModal() {
    document.getElementById('reservationModal').classList.add('hidden');
}

function openRulesModal() {
    document.getElementById('rulesModal').classList.remove('hidden');
}

function closeRulesModal() {
    document.getElementById('rulesModal').classList.add('hidden');
}

function openOrderHistoryModal() {
    document.getElementById('orderHistoryModal').classList.remove('hidden');
}

function closeOrderHistoryModal() {
    document.getElementById('orderHistoryModal').classList.add('hidden');
}

function closeSuccessModal() {
    document.getElementById('successModal').classList.add('hidden');
    window.location.href = "{{ url_for('reservations') }}";
}

function closeErrorModal() {
    document.getElementById('errorModal').classList.add('hidden');
}

// Order filtering functions
function filterOrders(status) {
    const orderItems = document.querySelectorAll('.order-item');
    const filterBtns = document.querySelectorAll('.filter-btn');

    // Update active button
    filterBtns.forEach(btn => {
        btn.classList.remove('active', 'bg-blue-600', 'text-white');
        btn.classList.add('bg-gray-200', 'text-gray-700');
    });
    event.target.classList.add('active', 'bg-blue-600', 'text-white');
    event.target.classList.remove('bg-gray-200', 'text-gray-700');

    // Filter orders
    orderItems.forEach(item => {
        if (status === 'all' || item.dataset.status === status) {
            item.style.display = 'block';
        } else {
            item.style.display = 'none';
        }
    });
}

// Rate reservation function
function rateReservation(reservationId) {
    // This would typically make an AJAX call to rate the reservation
    alert(`Rating reservation #${reservationId}. This would open a rating dialog.`);
}

// Cancel reservation function
function cancelReservation(reservationId) {
    if (confirm('Are you sure you want to cancel this reservation?')) {
        // This would typically make an AJAX call to cancel the reservation
        alert(`Cancelling reservation #${reservationId}. This would make an API call.`);
    }
}

// Handle form submissions with AJAX for better UX
document.addEventListener('DOMContentLoaded', function () {
    const forms = document.querySelectorAll('form[action*="reserve"]');
    forms.forEach(form => {
        form.addEventListener('submit', function (e) {
            e.preventDefault();

            const formData = new FormData(form);
            const url = form.action;

            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            })
                .then(response => {
                    if (response.ok) {
                        closeReservationModal();
                        document.getElementById('successModal').classList.remove('hidden');
                    } else {
                        return response.json();
                    }
                })
                .then(data => {
                    if (data && data.error) {
                        document.getElementById('errorMessage').textContent = data.error;
                        document.getElementById('errorModal').classList.remove('hidden');
                    }
                })
                .catch(error => {
                    // Error case
                    console.error('Error:', error);
                    const errorMessage = error.error || 'An unexpected error occurred';
                    document.getElementById('errorMessage').textContent = errorMessage;
                    document.getElementById('errorModal').classList.remove('hidden');
                })
                .finally(() => {
                    // Reset button state
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                });
        });
    });

    // Close modals when clicking outside of them
    const modals = document.querySelectorAll('[id$="Modal"]');
    modals.forEach(modal => {
        modal.addEventListener('click', function (e) {
            if (e.target === modal) {
                modal.classList.add('hidden');
            }
        });
    });

    // Close modals with Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape') {
            modals.forEach(modal => {
                if (!modal.classList.contains('hidden')) {
                    modal.classList.add('hidden');
                }
            });
        }
    });
});

// Additional utility functions

// Format date for display
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Validate form data before submission
function validateReservationForm(form) {
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('border-red-500');
            isValid = false;
        } else {
            field.classList.remove('border-red-500');
        }
    });

    return isValid;
}

// Show notification toast
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded-lg shadow-lg z-50 ${type === 'success' ? 'bg-green-500 text-white' :
            type === 'error' ? 'bg-red-500 text-white' :
                type === 'warning' ? 'bg-yellow-500 text-black' :
                    'bg-blue-500 text-white'
        }`;
    notification.textContent = message;

    document.body.appendChild(notification);

    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.remove();
    }, 5000);
}

// Export functions for global access
window.reservationSystem = {
    openReservationModal,
    closeReservationModal,
    openRulesModal,
    closeRulesModal,
    openOrderHistoryModal,
    closeOrderHistoryModal,
    closeSuccessModal,
    closeErrorModal,
    filterOrders,
    rateReservation,
    cancelReservation,
    formatDate,
    validateReservationForm,
    showNotification
};

// Add smooth scroll behavior
document.documentElement.style.scrollBehavior = 'smooth';