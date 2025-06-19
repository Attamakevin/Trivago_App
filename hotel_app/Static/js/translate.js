// SIMPLE SOLUTION: Just save language and apply it on every page load
function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: 'en,es,zh,de,it,pt,nl,ru,ja,ko',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');

    // Apply saved language immediately after Google Translate loads
    setTimeout(applySavedLanguage, 2000);
}

// Apply saved language on page load
function applySavedLanguage() {
    const savedLang = localStorage.getItem('user_language');

    if (savedLang && savedLang !== 'en') {
        console.log('Applying saved language:', savedLang);
        setGoogleTranslateLanguage(savedLang);
    }
}

// Set Google Translate to specific language
function setGoogleTranslateLanguage(langCode) {
    let attempts = 0;
    const maxAttempts = 15;

    const attemptTranslation = () => {
        const selectElement = document.querySelector('.goog-te-combo');

        if (selectElement && selectElement.options.length > 1) {
            console.log('Google Translate is ready. Available options:');

            // Log all options for debugging
            for (let i = 0; i < selectElement.options.length; i++) {
                console.log(i + ':', selectElement.options[i].value, '-', selectElement.options[i].text);
            }

            // Find and select the correct language
            let found = false;
            for (let i = 0; i < selectElement.options.length; i++) {
                const option = selectElement.options[i];
                const optionValue = option.value.toLowerCase();

                // Try exact match or partial match
                if (optionValue === langCode ||
                    optionValue === 'en|' + langCode ||
                    optionValue.endsWith('|' + langCode)) {

                    console.log('Setting language to:', option.value);
                    selectElement.value = option.value;

                    // Trigger change event
                    const event = new Event('change', { bubbles: true });
                    selectElement.dispatchEvent(event);

                    found = true;
                    break;
                }
            }

            if (!found) {
                console.log('Language not found:', langCode);
            }

            return found;
        } else {
            attempts++;
            if (attempts < maxAttempts) {
                console.log('Google Translate not ready, attempt', attempts);
                setTimeout(attemptTranslation, 500);
            } else {
                console.log('Failed to load Google Translate after', maxAttempts, 'attempts');
            }
        }
    };

    attemptTranslation();
}

// Save language when user changes it
function saveLanguageWhenChanged() {
    setTimeout(() => {
        const selectElement = document.querySelector('.goog-te-combo');
        if (selectElement) {
            selectElement.addEventListener('change', function () {
                let selectedLang = 'en';

                if (this.value && this.value.includes('|')) {
                    selectedLang = this.value.split('|')[1];
                } else if (this.value && this.value !== 'en') {
                    selectedLang = this.value;
                }

                console.log('User selected language:', selectedLang);
                localStorage.setItem('user_language', selectedLang);
            });
        }
    }, 3000);
}

document.addEventListener('DOMContentLoaded', function () {
    // Add CSS styles
    setTimeout(function () {
        const style = document.createElement('style');
        style.textContent = `
            /* Hide Google Translate banner */
            .goog-te-banner-frame { display: none !important; }
            body { top: 0 !important; }
            
            /* Desktop styling */
            .goog-te-gadget-simple {
                background: transparent !important;
                border: none !important;
            }
            
            .goog-te-gadget-simple .goog-te-menu-value span:first-child {
                display: none !important;
            }
            
            .goog-te-gadget-simple .goog-te-menu-value span:last-child {
                display: none !important;
            }
            
            .goog-te-gadget-simple .goog-te-menu-value {
                font-size: 0 !important;
                color: transparent !important;
                position: relative !important;
                padding: 8px !important;
                border-radius: 8px !important;
                transition: background-color 0.2s !important;
                min-width: 36px !important;
                height: 36px !important;
                display: inline-flex !important;
                align-items: center !important;
                justify-content: center !important;
            }
            
            .goog-te-gadget-simple .goog-te-menu-value::before {
                content: "🌐" !important;
                font-size: 20px !important;
                color: #374151 !important;
                position: absolute !important;
                top: 50% !important;
                left: 50% !important;
                transform: translate(-50%, -50%) !important;
            }
            
            .goog-te-gadget-simple .goog-te-menu-value:hover {
                background-color: #f3f4f6 !important;
            }
            
            .goog-te-combo {
                background-color: white !important;
                border: 1px solid #d1d5db !important;
                border-radius: 0.5rem !important;
                padding: 0.5rem 1rem !important;
                font-size: 14px !important;
                color: #374151 !important;
                outline: none !important;
            }
            
            /* Mobile-specific styling */
            @media screen and (max-width: 768px) {
                #google_translate_element {
                    margin-top: 8px !important;
                }
                .goog-te-gadget-simple {
                    background: transparent !important;
                    border: none !important;
                    font-size: 0 !important;
                }
                
                .goog-te-gadget-simple * {
                    font-size: 0 !important;
                    color: transparent !important;
                }
                
                .goog-te-gadget-simple .goog-te-menu-value {
                    width: 40px !important;
                    height: 40px !important;
                    padding: 10px !important;
                    border-radius: 50% !important;
                    background-color: #f8f9fa !important;
                    border: 1px solid #e9ecef !important;
                    display: flex !important;
                    align-items: center !important;
                    justify-content: center !important;
                    position: relative !important;
                }
                
                .goog-te-gadget-simple .goog-te-menu-value::before {
                    content: "🌐" !important;
                    font-size: 22px !important;
                    color: #495057 !important;
                    position: absolute !important;
                    top: 50% !important;
                    left: 50% !important;
                    transform: translate(-50%, -50%) !important;
                    z-index: 10 !important;
                }
                
                .goog-te-gadget-simple .goog-te-menu-value:active {
                    background-color: #e9ecef !important;
                    transform: scale(0.95) !important;
                }
                
                /* Hide all text elements on mobile */
                .goog-te-gadget-simple span,
                .goog-te-gadget-simple .goog-te-menu-value span {
                    display: none !important;
                    visibility: hidden !important;
                    opacity: 0 !important;
                }
            }
            
            /* Small mobile screens */
            @media screen and (max-width: 480px) {
                .goog-te-gadget-simple .goog-te-menu-value {
                    width: 36px !important;
                    height: 36px !important;
                    padding: 8px !important;
                }
                
                .goog-te-gadget-simple .goog-te-menu-value::before {
                    font-size: 18px !important;
                }
            }
        `;
        document.head.appendChild(style);
    }, 1000);

    // Setup language change monitoring
    saveLanguageWhenChanged();
});

// TEST FUNCTION - Open console and run this to test
function testLanguagePersistence() {
    console.log('=== LANGUAGE TEST ===');
    console.log('Saved language:', localStorage.getItem('user_language'));

    const select = document.querySelector('.goog-te-combo');
    if (select) {
        console.log('Google Translate current value:', select.value);
        console.log('Available options:');
        for (let i = 0; i < select.options.length; i++) {
            console.log(`${i}: ${select.options[i].value} - ${select.options[i].text}`);
        }
    } else {
        console.log('Google Translate not found');
    }

    console.log('To test: setGoogleTranslateLanguage("es")');
}