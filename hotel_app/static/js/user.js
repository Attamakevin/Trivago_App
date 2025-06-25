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

// Deposit Functionality
let selectedAmount = 0;
let selectedPaymentMethod = '';

function selectAmount(amount) {
    selectedAmount = amount;
    document.getElementById('customAmount').value = amount;

    // Update button styles
    document.querySelectorAll('.amount-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    event.target.classList.add('selected');

    updateSummary();
}

function selectPaymentMethod(method) {
    selectedPaymentMethod = method;

    // Update the actual radio input
    document.querySelector(`input[name="network"][value="${method}"]`).checked = true;

    // Update payment card styles
    document.querySelectorAll('.payment-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelectorAll('.payment-radio').forEach(radio => {
        radio.style.backgroundColor = 'transparent';
        radio.innerHTML = '';
        radio.classList.remove('checked');
    });

    // Find the parent label and mark as selected
    const radioInput = document.querySelector(`input[name="network"][value="${method}"]`);
    const parentLabel = radioInput.closest('.payment-card');
    parentLabel.classList.add('selected');

    // Update the visual radio button with BIGGER check mark
    const radioVisual = document.getElementById(method + '-radio');
    radioVisual.style.backgroundColor = '#3b82f6';
    radioVisual.innerHTML = '<i class="fas fa-check text-white text-xl"></i>'; // Changed from text-xs to text-base
    radioVisual.classList.add('checked');

    updateSummary();
}

function updateSummary() {
    const amount = parseFloat(document.getElementById('customAmount').value) || selectedAmount;
    const hasPaymentMethod = document.querySelector('input[name="network"]:checked');

    if (amount > 0 && hasPaymentMethod) {
        const fee = calculateFee(amount, hasPaymentMethod.value);
        const total = amount + fee;

        document.getElementById('summaryAmount').textContent = '$' + amount.toFixed(2);
        document.getElementById('summaryFee').textContent = '$' + fee.toFixed(2);
        document.getElementById('summaryTotal').textContent = '$' + total.toFixed(2);
        document.getElementById('summary').style.display = 'block';

        document.getElementById('depositBtn').disabled = false;
        document.getElementById('depositBtn').classList.remove('bg-gray-400');
        document.getElementById('depositBtn').classList.add('bg-blue-600', 'hover:bg-blue-700');
    } else {
        document.getElementById('summary').style.display = 'none';
        document.getElementById('depositBtn').disabled = true;
        document.getElementById('depositBtn').classList.add('bg-gray-400');
        document.getElementById('depositBtn').classList.remove('bg-blue-600', 'hover:bg-blue-700');
    }
}

function calculateFee(amount, method) {
    const fees = {
        'usdt': amount * 0.01,        // 1% fee for USDT
        'usdt1': amount * 0.015,      // 1.5% fee for USDT1
    };
    return fees[method] || 0;
}

function showStyledAlert(message, type = 'info', title = '', autoClose = false) {
    const alertConfig = {
        success: {
            bgColor: 'bg-green-100',
            iconColor: 'text-green-600',
            buttonColor: 'bg-green-600 hover:bg-green-700',
            icon: 'fa-check-circle',
            defaultTitle: 'Success!'
        },
        error: {
            bgColor: 'bg-red-100',
            iconColor: 'text-red-600',
            buttonColor: 'bg-red-600 hover:bg-red-700',
            icon: 'fa-exclamation-triangle',
            defaultTitle: 'Error'
        }
    };

    const config = alertConfig[type] || alertConfig.success;
    const alertTitle = title || config.defaultTitle;

    // Remove existing alert
    const existingAlert = document.getElementById('styledAlert');
    if (existingAlert) existingAlert.remove();

    const modalHTML = `
    <div id="styledAlert" data-type="${type}" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
        <div class="bg-white rounded-2xl shadow-xl max-w-md w-full transform transition-all duration-300">
            <div class="p-6 text-center">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center ${config.bgColor}">
                    <i class="fas ${config.icon} ${config.iconColor} text-2xl"></i>
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-3">${alertTitle}</h3>
                <p class="text-gray-600 mb-6">${message}</p>
                <button onclick="closeStyledAlert()" class="w-full ${config.buttonColor} text-white font-medium py-3 px-4 rounded-xl transition-colors">
                    OK
                </button>
            </div>
        </div>
    </div>
`;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeStyledAlert() {
    const modal = document.getElementById('styledAlert');
    if (modal) {
        const modalType = modal.dataset.type;
        modal.remove();

        // Only redirect on success
        if (modalType === 'success') {
            // Don't use history.back() here as it causes issues
            setTimeout(() => {
                window.location.href = '/profile'; // or wherever you want to redirect
            }, 500);
        }
    }
}

function showTelegramInstructions(amount, network) {
    const instructionHTML = `
        <div id="telegramModal" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl shadow-xl max-w-md w-full p-6 text-center">
                <div class="w-16 h-16 mx-auto mb-4 rounded-full bg-green-100 flex items-center justify-center">
                    <i class="fas fa-check text-green-600 text-2xl"></i>
                </div>
                <h3 class="text-xl font-bold text-gray-900 mb-4">Deposit Request Submitted!</h3>
                
                <div class="bg-gray-50 rounded-xl p-4 mb-4 text-left">
                    <p class="text-sm text-gray-600">Amount: <span class="font-medium">$${amount}</span></p>
                    <p class="text-sm text-gray-600">Network: <span class="font-medium">${network.toUpperCase()}</span></p>
                </div>
                
                <p class="text-sm text-gray-600 mb-6">Click below to contact our admin on Telegram to complete your deposit.</p>
                
                <div class="flex space-x-3">
                    <button onclick="closeTelegramModal()" 
                            class="flex-1 bg-gray-300 hover:bg-gray-400 text-gray-700 font-medium py-3 px-4 rounded-xl transition-colors">
                        Close
                    </button>
                    <button onclick="openTelegram()" 
                            class="flex-1 bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-4 rounded-xl transition-colors">
                        <i class="fab fa-telegram mr-2"></i>Open Telegram
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', instructionHTML);
}

function openTelegram() {
    window.open('https://t.me/your_admin_telegram', '_blank');
    closeTelegramModal();
    // Optionally redirect back to profile
    window.location.href = '/profile';
}

function closeTelegramModal() {
    const modal = document.getElementById('telegramModal');
    if (modal) modal.remove();
    // Optionally redirect back to profile
    window.location.href = '/profile';
}

function handleFormSubmit(event) {
    event.preventDefault();

    const amount = parseFloat(document.getElementById('customAmount').value) || selectedAmount;
    const networkInput = document.querySelector('input[name="network"]:checked');

    if (amount < 10) {
        showStyledAlert('Minimum deposit amount is $10.00', 'error');
        return false;
    }

    if (amount > 10000) {
        showStyledAlert('Maximum deposit amount is $10,000.00', 'error');
        return false;
    }

    if (!networkInput) {
        showStyledAlert('Please select a payment method', 'error');
        return false;
    }

    // Show loading state
    const btn = document.getElementById('depositBtn');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i><span>Processing...</span>';
    btn.disabled = true;

    // Submit form in background using fetch
    const formData = new FormData(event.target);

    fetch('/deposit', {
        method: 'POST',
        body: formData
    })
        .then(response => {
            if (response.ok) {
                // Show Telegram instructions modal instead of redirecting
                showTelegramInstructions(amount, networkInput.value);
            } else {
                showStyledAlert('An error occurred processing your deposit', 'error');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            showStyledAlert('An error occurred processing your deposit', 'error');
        })
        .finally(() => {
            // Reset button state
            btn.innerHTML = '<i class="fas fa-plus"></i><span>Add Funds</span>';
            btn.disabled = false;
        });

    return false;
}

// Listen for custom amount input
document.addEventListener('DOMContentLoaded', function () {
    const customAmountInput = document.getElementById('customAmount');
    if (customAmountInput) {
        customAmountInput.addEventListener('input', function () {
            selectedAmount = parseFloat(this.value) || 0;

            // Clear quick amount selection
            document.querySelectorAll('.amount-btn').forEach(btn => {
                btn.classList.remove('selected');
            });

            updateSummary();
        });
    }

    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
});

// Close on background click
document.addEventListener('click', function (event) {
    if (event.target && event.target.id === 'styledAlert') {
        closeStyledAlert();
    }
});

// Close on Escape key
document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && document.getElementById('styledAlert')) {
        closeStyledAlert();
    }
});


// Clipboard functionality
function copyToClipboard(text, buttonElement = null) {
    // Try modern clipboard API first
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showCopySuccess(buttonElement);
        }).catch(() => {
            // Fallback to older method
            copyTextFallback(text, buttonElement);
        });
    } else {
        // Fallback for older browsers or non-secure contexts
        copyTextFallback(text, buttonElement);
    }
}

function copyTextFallback(text, buttonElement) {
    const textArea = document.createElement('textarea');
    textArea.value = text;
    textArea.style.position = 'fixed';
    textArea.style.left = '-999999px';
    textArea.style.top = '-999999px';
    document.body.appendChild(textArea);
    textArea.focus();
    textArea.select();

    try {
        document.execCommand('copy');
        showCopySuccess(buttonElement);
    } catch (err) {
        showWithdrawAlert('Failed to copy to clipboard', 'error');
    } finally {
        document.body.removeChild(textArea);
    }
}

function showCopySuccess(buttonElement) {
    if (buttonElement) {
        const originalHTML = buttonElement.innerHTML;
        buttonElement.innerHTML = '<i class="fas fa-check text-green-600"></i> Copied!';
        buttonElement.classList.add('text-green-600');

        setTimeout(() => {
            buttonElement.innerHTML = originalHTML;
            buttonElement.classList.remove('text-green-600');
        }, 2000);
    } else {
        // Show a toast notification
        showCopyToast();
    }
}

function showCopyToast() {
    const toast = document.createElement('div');
    toast.className = 'fixed top-4 right-4 bg-green-600 text-white px-4 py-2 rounded-lg shadow-lg z-50 transform translate-x-full transition-transform duration-300';
    toast.innerHTML = '<i class="fas fa-check mr-2"></i>Copied to clipboard!';

    document.body.appendChild(toast);

    // Slide in
    setTimeout(() => {
        toast.classList.remove('translate-x-full');
    }, 10);

    // Slide out and remove
    setTimeout(() => {
        toast.classList.add('translate-x-full');
        setTimeout(() => {
            document.body.removeChild(toast);
        }, 300);
    }, 2000);
}


// Withdraw Functionality
let withdrawSelectedAmount = 0;
let selectedWithdrawMethod = '';
const availableBalance = parseFloat('{{ user.balance|float }}');

function selectWithdrawAmount(amount) {
    withdrawSelectedAmount = amount;
    document.getElementById('customAmount').value = amount;

    // Update button styles
    document.querySelectorAll('.amount-btn').forEach(btn => {
        btn.classList.remove('selected');
    });
    event.target.classList.add('selected');

    updateWithdrawSummary();
}

function selectWithdrawMethod(method) {
    selectedWithdrawMethod = method;

    // Map the method to the correct radio value
    const methodMap = {
        'withdraw_usdt': 'usdt',
        'withdraw_usdt1': 'usdt1'
    };

    const radioValue = methodMap[method] || method;

    // Update the actual radio input
    const radioInput = document.querySelector(`input[name="network"][value="${radioValue}"]`);
    if (radioInput) {
        radioInput.checked = true;
    }

    // Update payment card styles
    document.querySelectorAll('.withdraw-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelectorAll('.withdraw-radio').forEach(radio => {
        radio.style.backgroundColor = 'transparent';
        radio.innerHTML = '';
        radio.classList.remove('checked');
    });

    // Find the parent label and mark as selected
    if (radioInput) {
        const parentLabel = radioInput.closest('.withdraw-card');
        if (parentLabel) {
            parentLabel.classList.add('selected');
        }
    }

    // Update the visual radio button
    const radioVisual = document.getElementById(method + '-radio');
    radioVisual.style.backgroundColor = '#10b981';
    radioVisual.innerHTML = '<i class="fas fa-check text-white text-base"></i>';
    radioVisual.classList.add('checked');

    updateWithdrawSummary();
}

function updateWithdrawSummary() {
    const amount = parseFloat(document.getElementById('customAmount').value) || withdrawSelectedAmount;
    const hasPaymentMethod = document.querySelector('input[name="network"]:checked');
    const hasWalletAddress = document.getElementById('walletAddress').value.trim();

    // Check if amount exceeds balance
    if (amount > availableBalance) {
        showWithdrawAlert(`Insufficient funds. Your available balance is ${availableBalance.toFixed(2)}`, 'error', 'Insufficient Balance');
        // Clear the input
        document.getElementById('customAmount').value = '';
        withdrawSelectedAmount = 0;
        // Clear amount button selections
        document.querySelectorAll('.amount-btn').forEach(btn => {
            btn.classList.remove('selected');
        });
        return;
        }

    if (amount > 0 && hasPaymentMethod && hasWalletAddress) {
        const fee = calculateWithdrawFee(amount, hasPaymentMethod.value);
        const total = amount - fee;

        document.getElementById('summaryAmount').textContent = '$' + amount.toFixed(2);
        document.getElementById('summaryFee').textContent = '$' + fee.toFixed(2);
        document.getElementById('summaryTotal').textContent = '$' + total.toFixed(2);
        document.getElementById('summary').style.display = 'block';

        document.getElementById('withdrawBtn').disabled = false;
        document.getElementById('withdrawBtn').classList.remove('bg-gray-400');
        document.getElementById('withdrawBtn').classList.add('bg-green-600', 'hover:bg-green-700');
    } else {
        document.getElementById('summary').style.display = 'none';
        document.getElementById('withdrawBtn').disabled = true;
        document.getElementById('withdrawBtn').classList.add('bg-gray-400');
        document.getElementById('withdrawBtn').classList.remove('bg-green-600', 'hover:bg-green-700');
    }
}

function calculateWithdrawFee(amount, method) {
    const fees = {
        'usdt': amount * 0.01,        // 1% fee for USDT
        'usdt1': amount * 0.015,      // 1.5% fee for USDT1
    };
    return fees[method] || 0;
}

function showWithdrawAlert(message, type = 'info', title = '', autoClose = false) {
    const alertConfig = {
        success: {
            bgColor: 'bg-green-100',
            iconColor: 'text-green-600',
            buttonColor: 'bg-green-600 hover:bg-green-700',
            icon: 'fa-check-circle',
            defaultTitle: 'Success!'
        },
        error: {
            bgColor: 'bg-red-100',
            iconColor: 'text-red-600',
            buttonColor: 'bg-red-600 hover:bg-red-700',
            icon: 'fa-exclamation-triangle',
            defaultTitle: 'Error'
        }
    };

    const config = alertConfig[type] || alertConfig.success;
    const alertTitle = title || config.defaultTitle;

    // Remove existing alert
    const existingAlert = document.getElementById('withdrawStyledAlert');
    if (existingAlert) existingAlert.remove();

    const modalHTML = `
        <div id="withdrawStyledAlert" data-type="${type}" class="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
            <div class="bg-white rounded-2xl shadow-xl max-w-md w-full transform transition-all duration-300">
                <div class="p-6 text-center">
                    <div class="w-16 h-16 mx-auto mb-4 rounded-full flex items-center justify-center ${config.bgColor}">
                        <i class="fas ${config.icon} ${config.iconColor} text-2xl"></i>
                    </div>
                    <h3 class="text-xl font-bold text-gray-900 mb-3">${alertTitle}</h3>
                    <p class="text-gray-600 mb-6">${message}</p>
                    <button onclick="closeWithdrawAlert()" class="w-full ${config.buttonColor} text-white font-medium py-3 px-4 rounded-xl transition-colors">
                        OK
                    </button>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function closeWithdrawAlert() {
    const modal = document.getElementById('withdrawStyledAlert');
    if (modal) {
        const modalType = modal.dataset.type;
        modal.remove();

        if (modalType === 'success') {
            setTimeout(() => {
                window.location.href = '/profile';
            }, 500);
        }
    }
}

function handleWithdrawFormSubmit(event) {
    event.preventDefault();

    const amount = parseFloat(document.getElementById('customAmount').value) || withdrawSelectedAmount;
    const networkInput = document.querySelector('input[name="network"]:checked');
    const walletAddress = document.getElementById('walletAddress').value.trim();

    if (amount < 25) {
        window.showWithdrawAlert('Minimum withdrawal amount is $25.00', 'error');
        return false;
    }

    if (amount > availableBalance) {
        window.showWithdrawAlert(`Insufficient funds. Your available balance is $${availableBalance.toFixed(2)}`, 'error');
        return false;
    }

    if (!networkInput) {
        window.showWithdrawAlert('Please select a withdrawal method', 'error');
        return false;
    }

    if (!walletAddress) {
        window.showWithdrawAlert('Please enter your wallet address', 'error');
        return false;
    }

    if (walletAddress.length < 10) {
        window.showWithdrawAlert('Please enter a valid wallet address', 'error');
        return false;
    }

    // Show loading state
    const btn = document.getElementById('withdrawBtn');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i><span>Processing...</span>';
    btn.disabled = true;

    // Submit the form
    setTimeout(() => {
        event.target.submit();
    }, 1000);

    return false;
}

// Withdraw-specific event listeners
function initializeWithdrawEvents() {
    const customAmountInput = document.getElementById('customAmount');
    const walletInput = document.getElementById('walletAddress');

    if (customAmountInput) {
        customAmountInput.addEventListener('input', function () {
            withdrawSelectedAmount = parseFloat(this.value) || 0;

            // Clear quick amount selection
            document.querySelectorAll('.amount-btn').forEach(btn => {
                btn.classList.remove('selected');
            });

            updateWithdrawSummary();
        });
    }

    if (walletInput) {
        walletInput.addEventListener('input', updateWithdrawSummary);
    }

    // Close on background click for withdraw alerts
    document.addEventListener('click', function (event) {
        if (event.target && event.target.id === 'withdrawStyledAlert') {
            closeWithdrawAlert();
        }
    });

    // Close on Escape key for withdraw alerts
    document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && document.getElementById('withdrawStyledAlert')) {
            closeWithdrawAlert();
        }
    });

    // Add smooth scroll behavior
    document.documentElement.style.scrollBehavior = 'smooth';
}

// Add smooth scroll behavior
document.documentElement.style.scrollBehavior = 'smooth';
