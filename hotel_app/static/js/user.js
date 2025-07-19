// Universal Slider JavaScript - Works with any number of slides
document.addEventListener('DOMContentLoaded', function () {
    let currentSlideIndex = 0;
    let isAutoPlaying = true;
    let autoplayInterval;

    // Select elements - now looks for both 'slide' and 'event-slide' classes
    let slides = document.querySelectorAll('.slide');
    if (slides.length === 0) {
        slides = document.querySelectorAll('.event-slide');
    }

    const indicators = document.querySelectorAll('.indicator');
    const sliderContainer = document.querySelector('.relative');
    const totalSlides = slides.length;

    // console.log('Found', totalSlides, 'slides and', indicators.length, 'indicators');

    if (totalSlides === 0) {
        // console.error('No slides found! Check HTML structure.');
        return;
    }

    // Auto-generate indicators if they don't match slide count
    function generateIndicators() {
        const indicatorContainer = document.querySelector('.indicator')?.parentElement;
        if (indicatorContainer && indicators.length !== totalSlides) {
            // Clear existing indicators
            indicatorContainer.innerHTML = '';

            // Generate new indicators to match slide count
            for (let i = 0; i < totalSlides; i++) {
                const indicator = document.createElement('button');
                indicator.onclick = () => goToSlide(i);
                indicator.className = `w-3 h-3 md:w-4 md:h-4 rounded-full bg-white transition-all duration-300 indicator ${i === 0 ? 'scale-110' : 'bg-opacity-50'}`;
                indicatorContainer.appendChild(indicator);
            }

            // Update indicators NodeList
            return document.querySelectorAll('.indicator');
        }
        return indicators;
    }

    // Generate indicators if needed
    const updatedIndicators = generateIndicators();

    // Show specific slide
    function showSlide(index) {
        // Ensure index is within bounds
        if (index < 0 || index >= totalSlides) return;

        // Remove active class from all slides and indicators
        slides.forEach((slide, i) => {
            slide.classList.remove('active', 'prev');
            // Handle both class naming conventions
            if (slide.classList.contains('event-slide')) {
                slide.style.opacity = i === index ? '1' : '0';
            }
        });

        updatedIndicators.forEach(indicator => {
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
            // Ensure visibility for event-slide class
            if (slides[currentSlideIndex].classList.contains('event-slide')) {
                slides[currentSlideIndex].style.opacity = '1';
            }
        }

        if (updatedIndicators[currentSlideIndex]) {
            updatedIndicators[currentSlideIndex].classList.remove('bg-opacity-50');
            updatedIndicators[currentSlideIndex].classList.add('bg-white', 'scale-110');
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

        if (playIcon && pauseIcon) {
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
    }

    // Initialize slider
    function initSlider() {
        // console.log('Initializing slider with', totalSlides, 'slides');
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

    // Progress bars animation (if they exist)
    const progressBars = document.querySelectorAll('.progress-fill');
    progressBars.forEach(bar => {
        const width = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = width;
        }, 500);
    });
});

// Reservation Page Functionality



// Simplified Deposit Functionality
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

    // Update the visual radio button with check mark
    const radioVisual = document.getElementById(method + '-radio');
    radioVisual.style.backgroundColor = '#3b82f6';
    radioVisual.innerHTML = '<i class="fas fa-check text-white text-xl"></i>';
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

        // Enable submit button
        document.getElementById('depositBtn').disabled = false;
        document.getElementById('depositBtn').classList.remove('bg-gray-400');
        document.getElementById('depositBtn').classList.add('bg-blue-600', 'hover:bg-blue-700');
    } else {
        document.getElementById('summary').style.display = 'none';

        // Disable submit button
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

function handleFormSubmit(event) {
    event.preventDefault();

    const amount = parseFloat(document.getElementById('customAmount').value) || selectedAmount;
    const networkInput = document.querySelector('input[name="network"]:checked');

    // Basic validation
    if (amount < 10) {
        alert('Minimum deposit amount is $10.00');
        return false;
    }

    if (amount > 10000) {
        alert('Maximum deposit amount is $10,000.00');
        return false;
    }

    if (!networkInput) {
        alert('Please select a payment method');
        return false;
    }

    // Show loading state
    const btn = document.getElementById('depositBtn');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i><span>Processing...</span>';
    btn.disabled = true;

    // Submit the form data to backend first
    const form = event.target;
    const formData = new FormData(form);

    fetch('/deposit', {
        method: 'POST',
        body: formData
    })
        .then(response => response.text())
        .then(result => {
            // After successful submission to backend, redirect to customer service
            // console.log('Deposit submitted successfully');
            window.location.href = '/customer_service';
        })
        .catch(error => {
            // console.error('Error:', error);
            alert('Error submitting deposit. Please try again.');

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
        alert('Minimum withdrawal amount is $25.00', 'error');
        return false;
    }

    if (amount > availableBalance) {
        alert(`Insufficient funds. Your available balance is $${availableBalance.toFixed(2)}`, 'error');
        return false;
    }

    if (!networkInput) {
        alert('Please select a withdrawal method', 'error');
        return false;
    }

    if (!walletAddress) {
        alert('Please enter your wallet address', 'error');
        return false;
    }

    if (walletAddress.length < 10) {
        alert('Please enter a valid wallet address', 'error');
        return false;
    }

    // Show loading state
    const btn = document.getElementById('withdrawBtn');
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i><span>Processing...</span>';
    btn.disabled = true;

    // Submit the form
    setTimeout(() => {
        // Instead of just submitting, show success message first
        showWithdrawAlert('Withdrawal request submitted successfully! You will be redirected to your profile.', 'success');

        // Then submit after a delay
        setTimeout(() => {
            event.target.submit();
        }, 2000);
    }, 1000);
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

// Feedback Form Functionality

let currentRating = 0;
let uploadedImages = [];

// Character counter
document.getElementById('feedbackMessage').addEventListener('input', function () {
    const charCount = this.value.length;
    document.getElementById('charCount').textContent = `${charCount} characters`;

    if (charCount < 20) {
        document.getElementById('charCount').className = 'text-xs text-red-400';
    } else {
        document.getElementById('charCount').className = 'text-xs text-gray-400';
    }
});

// Star rating functionality
function setRating(rating) {
    currentRating = rating;
    const stars = document.querySelectorAll('.star');
    const ratingTexts = ['', 'Poor', 'Fair', 'Good', 'Very Good', 'Excellent'];

    stars.forEach((star, index) => {
        if (index < rating) {
            star.className = 'star cursor-pointer text-2xl text-yellow-400 transition-colors';
        } else {
            star.className = 'star cursor-pointer text-2xl text-gray-300 hover:text-yellow-400 transition-colors';
        }
    });

    document.getElementById('ratingText').textContent = ratingTexts[rating];
}

// Image upload handling
function handleImageUpload(event) {
    const files = Array.from(event.target.files);
    const maxFiles = 5;
    const maxSize = 5 * 1024 * 1024; // 5MB

    if (uploadedImages.length + files.length > maxFiles) {
        alert(`You can only upload up to ${maxFiles} images.`);
        return;
    }

    files.forEach(file => {
        if (file.size > maxSize) {
            alert(`${file.name} is too large. Maximum file size is 5MB.`);
            return;
        }

        if (!file.type.startsWith('image/')) {
            alert(`${file.name} is not a valid image file.`);
            return;
        }

        uploadedImages.push(file);

        // Create preview
        const reader = new FileReader();
        reader.onload = function (e) {
            addImagePreview(e.target.result, file.name, uploadedImages.length - 1);
        };
        reader.readAsDataURL(file);
    });

    // Clear the input
    event.target.value = '';
}

function addImagePreview(src, name, index) {
    const previewContainer = document.getElementById('imagePreview');
    previewContainer.classList.remove('hidden');

    const imageDiv = document.createElement('div');
    imageDiv.className = 'relative group';
    imageDiv.innerHTML = `
                <img src="${src}" alt="${name}" class="w-full h-20 object-cover rounded-lg border border-gray-200">
                <button type="button" onclick="removeImage(${index})" 
                        class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-xs hover:bg-red-600 transition-colors opacity-0 group-hover:opacity-100">
                    <i class="fas fa-times"></i>
                </button>
                <div class="absolute bottom-0 left-0 right-0 bg-black bg-opacity-75 text-white text-xs p-1 rounded-b-lg truncate">
                    ${name}
                </div>
            `;

    previewContainer.appendChild(imageDiv);
}

function removeImage(index) {
    uploadedImages.splice(index, 1);

    // Rebuild preview
    const previewContainer = document.getElementById('imagePreview');
    previewContainer.innerHTML = '';

    if (uploadedImages.length === 0) {
        previewContainer.classList.add('hidden');
    } else {
        uploadedImages.forEach((file, i) => {
            const reader = new FileReader();
            reader.onload = function (e) {
                addImagePreview(e.target.result, file.name, i);
            };
            reader.readAsDataURL(file);
        });
    }
}

// Form submission
function submitFeedback(event) {
    event.preventDefault();

    const name = document.getElementById('userName').value;
    const email = document.getElementById('userEmail').value;
    const type = document.getElementById('feedbackType').value;
    const subject = document.getElementById('feedbackSubject').value;
    const message = document.getElementById('feedbackMessage').value;
    const contactMe = document.getElementById('contactMe').checked;

    // Validation
    if (message.length < 20) {
        alert('Please provide at least 20 characters in your feedback message.');
        return;
    }

    // Simulate form submission
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin mr-2"></i>Submitting...';
    submitBtn.disabled = true;

    setTimeout(() => {
        // Reset submit button first
        submitBtn.innerHTML = '<i class="fas fa-paper-plane mr-2"></i>Submit Feedback';
        submitBtn.disabled = false;

        // Show success message
        const successMessage = document.getElementById('successMessage');
        successMessage.classList.remove('hidden');
        successMessage.scrollIntoView({ behavior: 'smooth' });

        // Reset form after showing success message
        setTimeout(() => {
            resetForm();
        }, 1000);
    }, 2000);
}

// Reset form
function resetForm() {
    // Don't hide success message when called from submit function
    const isFormSubmitted = !document.getElementById('successMessage').classList.contains('hidden');

    document.querySelector('form').reset();
    currentRating = 0;
    uploadedImages = [];

    // Reset stars
    document.querySelectorAll('.star').forEach(star => {
        star.className = 'star cursor-pointer text-2xl text-gray-300 hover:text-yellow-400 transition-colors';
    });
    document.getElementById('ratingText').textContent = '';

    // Reset character count
    document.getElementById('charCount').textContent = '0 characters';
    document.getElementById('charCount').className = 'text-xs text-gray-400';

    // Reset image preview
    document.getElementById('imagePreview').innerHTML = '';
    document.getElementById('imagePreview').classList.add('hidden');

    // Only hide success message if this is a manual reset (not from form submission)
    if (!isFormSubmitted) {
        document.getElementById('successMessage').classList.add('hidden');
    }
}

// Drag and drop functionality
const uploadArea = document.querySelector('.border-dashed');

uploadArea.addEventListener('dragover', function (e) {
    e.preventDefault();
    this.classList.add('border-orange-400', 'bg-orange-50');
});

uploadArea.addEventListener('dragleave', function (e) {
    e.preventDefault();
    this.classList.remove('border-orange-400', 'bg-orange-50');
});

uploadArea.addEventListener('drop', function (e) {
    e.preventDefault();
    this.classList.remove('border-orange-400', 'bg-orange-50');

    const files = e.dataTransfer.files;
    document.getElementById('imageUpload').files = files;
    handleImageUpload({ target: { files: files } });
});

// Add smooth scroll behavior
document.documentElement.style.scrollBehavior = 'smooth';
