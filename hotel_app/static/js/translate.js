// AUTOMATIC STATIC TRANSLATION GENERATOR
// This will generate and save translations for all languages automatically

const AutoStaticTranslationGenerator = {
    // All world languages
    supportedLanguages: {
        'en': { name: 'English', flag: 'us', code: 'EN' },
        'zh': { name: 'Chinese', flag: 'cn', code: 'ZH' },
        'es': { name: 'Spanish', flag: 'es', code: 'ES' },
        'hi': { name: 'Hindi', flag: 'in', code: 'HI' },
        'ar': { name: 'Arabic', flag: 'sa', code: 'AR' },
        'pt': { name: 'Portuguese', flag: 'pt', code: 'PT' },
        'bn': { name: 'Bengali', flag: 'bd', code: 'BN' },
        'ru': { name: 'Russian', flag: 'ru', code: 'RU' },
        'ja': { name: 'Japanese', flag: 'jp', code: 'JA' },
        'de': { name: 'German', flag: 'de', code: 'DE' },
        'ko': { name: 'Korean', flag: 'kr', code: 'KO' },
        'fr': { name: 'French', flag: 'fr', code: 'FR' },
        'tr': { name: 'Turkish', flag: 'tr', code: 'TR' },
        'vi': { name: 'Vietnamese', flag: 'vn', code: 'VI' },
        'it': { name: 'Italian', flag: 'it', code: 'IT' },
        'th': { name: 'Thai', flag: 'th', code: 'TH' },
        'pl': { name: 'Polish', flag: 'pl', code: 'PL' },
        'uk': { name: 'Ukrainian', flag: 'ua', code: 'UK' },
        'nl': { name: 'Dutch', flag: 'nl', code: 'NL' },
        'ro': { name: 'Romanian', flag: 'ro', code: 'RO' },
        'hu': { name: 'Hungarian', flag: 'hu', code: 'HU' },
        'cs': { name: 'Czech', flag: 'cz', code: 'CS' },
        'sv': { name: 'Swedish', flag: 'se', code: 'SV' },
        'el': { name: 'Greek', flag: 'gr', code: 'EL' },
        'he': { name: 'Hebrew', flag: 'il', code: 'HE' },
        'da': { name: 'Danish', flag: 'dk', code: 'DA' },
        'fi': { name: 'Finnish', flag: 'fi', code: 'FI' },
        'no': { name: 'Norwegian', flag: 'no', code: 'NO' },
        'id': { name: 'Indonesian', flag: 'id', code: 'ID' },
        'ms': { name: 'Malay', flag: 'my', code: 'MS' },
        'tl': { name: 'Filipino', flag: 'ph', code: 'TL' },
        'fa': { name: 'Persian', flag: 'ir', code: 'FA' },
        'sw': { name: 'Swahili', flag: 'ke', code: 'SW' },
        'ta': { name: 'Tamil', flag: 'in', code: 'TA' },
        'te': { name: 'Telugu', flag: 'in', code: 'TE' },
        'mr': { name: 'Marathi', flag: 'in', code: 'MR' },
        'ur': { name: 'Urdu', flag: 'pk', code: 'UR' },
        'gu': { name: 'Gujarati', flag: 'in', code: 'GU' },
        'kn': { name: 'Kannada', flag: 'in', code: 'KN' },
        'ml': { name: 'Malayalam', flag: 'in', code: 'ML' },
        'pa': { name: 'Punjabi', flag: 'in', code: 'PA' },
        'bg': { name: 'Bulgarian', flag: 'bg', code: 'BG' },
        'hr': { name: 'Croatian', flag: 'hr', code: 'HR' },
        'sk': { name: 'Slovak', flag: 'sk', code: 'SK' },
        'lt': { name: 'Lithuanian', flag: 'lt', code: 'LT' },
        'sl': { name: 'Slovenian', flag: 'si', code: 'SL' },
        'lv': { name: 'Latvian', flag: 'lv', code: 'LV' },
        'et': { name: 'Estonian', flag: 'ee', code: 'ET' },
        'sr': { name: 'Serbian', flag: 'rs', code: 'SR' },
        'af': { name: 'Afrikaans', flag: 'za', code: 'AF' },
        'sq': { name: 'Albanian', flag: 'al', code: 'SQ' },
        'hy': { name: 'Armenian', flag: 'am', code: 'HY' },
        'az': { name: 'Azerbaijani', flag: 'az', code: 'AZ' },
        'ka': { name: 'Georgian', flag: 'ge', code: 'KA' },
        'is': { name: 'Icelandic', flag: 'is', code: 'IS' },
        'km': { name: 'Khmer', flag: 'kh', code: 'KM' },
        'lo': { name: 'Lao', flag: 'la', code: 'LO' },
        'mk': { name: 'Macedonian', flag: 'mk', code: 'MK' },
        'mn': { name: 'Mongolian', flag: 'mn', code: 'MN' },
        'ne': { name: 'Nepali', flag: 'np', code: 'NE' },
        'si': { name: 'Sinhala', flag: 'lk', code: 'SI' },
        'zu': { name: 'Zulu', flag: 'za', code: 'ZU' }
    },

    // Master list of all English phrases to translate
    masterPhrases: [
        // Navigation & UI
        'trivago - Rate hotels worldwide',
        'Favorites',
        'Log in',
        'Menu',
        'Sign In / Register',
        'Sign In',
        'Sign Up',
        'Sign Out',
        'Back to Home',
        
        // Main content
        'Save up to 45% on your next hotel stay','Hot hotel deals right now',
        'We compare hotel prices from over 100 sites',
        'Hotel',
        'Places you recently searched',
        'Check in',
        'Check out',
        'Guests and rooms',
        'Search',
        'Adults',
        'Children',
        'Rooms',
        'Pet-friendly',
        'Apply',
        'RESET',
        
        // Hotel details
        'Excellent',
        'Very good',
        'per night',
        'Free cancellation',
        'Pay at the property',
        'Check deal',
        'Less than usual',
        
        // Account
        'Profile',
        'Settings',
        'Account Balance',
        'Current Balance',
        'Available Balance',
        'Total Deposits',
        'Total Withdrawals',
        'Transaction History',
        'Recent Transactions',
        
        // Actions
        'Add Funds',
        'Withdraw Funds',
        'Make a Deposit',
        'Make a Withdrawal',
        'Deposit',
        'Withdrawal',
        'Confirm',
        'Cancel',
        'Submit',
        'Reset',
        'Update',
        'Save',
        'Delete',
        'Edit',
        'View',
        'Close',
        
        // Forms
        'Name',
        'Email',
        'Phone Number',
        'Password',
        'Confirm Password',
        'Enter your password',
        'Enter new password',
        'Confirm new password',
        'Remember me',
        'Forgot password?',
        
        // Status
        'Success!',
        'Error',
        'Loading...',
        'Processing',
        'Completed',
        'Pending',
        'Cancelled',
        'Failed',
        'Approved',
        'Rejected',
        
        // Common words
        'Yes',
        'No',
        'OK',
        'All',
        'None',
        'Total',
        'Amount',
        'Date',
        'Time',
        'Today',
        'Yesterday',
        'This Week',
        'This Month',
        'This Year',
        'All Time',
        
        // Messages
        'Operation completed successfully.',
        'An error occurred. Please try again.',
        'Please fill in all required fields.',
        'Invalid input. Please check and try again.',
        'Are you sure you want to continue?',
        'Changes saved successfully.',
        'No data available.',
        'Loading data...',
        
        // Wallet & Payments
        'Wallet Address',
        'Enter your wallet address',
        'Payment Method',
        'Transaction ID',
        'Processing Fee',
        'Network',
        'Hash',
        'Fee',
        'Status',
        
        // Membership
        'Membership',
        'VIP Level',
        'Membership Levels',
        'Current',
        'Activated',
        'Not Activated',
        'Premium',
        'Exclusive',
        
        // Customer Support
        'Customer Support',
        'Need Help?',
        'Contact Us',
        'FAQs',
        'Help Center',
        'Support Team',
        
        // Reservations
        'Hotel Reservation Center',
        'Make Reservation',
        'Order History',
        'Reservation Successful!',
        'Reservation Failed',
        'Complete Reservation',
        'Commission',
        'Reserve Now',
        
        // Security
        'Security Verification',
        'Security Protection',
        'Set Withdrawal Password',
        'Change Login Password',
        'Password Requirements',
        'Important Security Notice',
        
        // Settings
        'Language Preferences',
        'Choose your preferred language',
        'Select Language',
        
        // Feedback
        'Feedback',
        'Share Your Feedback',
        'Your thoughts help us improve our service',
        'Feedback Type',
        'General Feedback',
        'Bug Report',
        'Feature Request',
        'Complaint',
        'Suggestion',
        'Subject',
        'Your Feedback',
        'Submit Feedback',
        
        // Credit Score
        'Credit Score',
        'Your Credit Score',
        'Credit Range',
        'Your Score',
        'What is Credit Score',
        
        // Time periods
        'Monday',
        'Tuesday',
        'Wednesday',
        'Thursday',
        'Friday',
        'Saturday',
        'Sunday'
    ],


    // Translate a single phrase
    async translatePhrase(text, targetLanguage) {
        try {
            const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=${targetLanguage}&dt=t&q=${encodeURIComponent(text)}`;
            const response = await fetch(url);
            const data = await response.json();
            return data[0].map(item => item[0]).join('');
        } catch (error) {
            console.error(`Translation error for "${text}":`, error);
            return text;
        }
    },

    // Generate translations for one language
    async generateLanguageTranslations(languageCode, languageName) {
        console.log(`📝 Generating translations for ${languageName}...`);
        
        const translations = {};
        const totalPhrases = this.masterPhrases.length;
        let completed = 0;

        const batchSize = 5;
        for (let i = 0; i < totalPhrases; i += batchSize) {
            const batch = this.masterPhrases.slice(i, i + batchSize);
            
            await Promise.all(batch.map(async (phrase) => {
                const translated = await this.translatePhrase(phrase, languageCode);
                translations[phrase] = translated;
                completed++;
                
                const progress = Math.round((completed / totalPhrases) * 100);
                console.log(`  Progress: ${progress}% (${completed}/${totalPhrases})`);
            }));
            
            if (i + batchSize < totalPhrases) {
                await this.delay(500);
            }
        }

        console.log(`✅ Completed ${languageName}!`);
        return translations;
    },

    // Save to localStorage
    saveToLocalStorage(languageCode, translations) {
        try {
            const key = `translations_${languageCode}`;
            localStorage.setItem(key, JSON.stringify(translations));
            console.log(`💾 Saved ${languageCode} to localStorage`);
        } catch (error) {
            console.error(`Error saving ${languageCode}:`, error);
        }
    },

    // Load from localStorage
    loadFromLocalStorage(languageCode) {
        try {
            const key = `translations_${languageCode}`;
            const stored = localStorage.getItem(key);
            return stored ? JSON.parse(stored) : null;
        } catch (error) {
            console.error(`Error loading ${languageCode}:`, error);
            return null;
        }
    },

    // Helper delay function
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// OPTIMIZED STATIC TRANSLATION SYSTEM (Uses pre-generated translations)
const FastStaticTranslationSystem = {
    config: {
        defaultLanguage: 'en',
        persistLanguage: true,
        storageKey: 'selectedLanguage',
        useLocalStorageCache: true
    },

    languages: {
        'en': { name: 'English', flag: 'us', code: 'EN' },
        'zh': { name: 'Chinese', flag: 'cn', code: 'ZH' },
        'es': { name: 'Spanish', flag: 'es', code: 'ES' },
        'hi': { name: 'Hindi', flag: 'in', code: 'HI' },
        'ar': { name: 'Arabic', flag: 'sa', code: 'AR' },
        'pt': { name: 'Portuguese', flag: 'pt', code: 'PT' },
        'bn': { name: 'Bengali', flag: 'bd', code: 'BN' },
        'ru': { name: 'Russian', flag: 'ru', code: 'RU' },
        'ja': { name: 'Japanese', flag: 'jp', code: 'JA' },
        'de': { name: 'German', flag: 'de', code: 'DE' },
        'ko': { name: 'Korean', flag: 'kr', code: 'KO' },
        'fr': { name: 'French', flag: 'fr', code: 'FR' },
        'tr': { name: 'Turkish', flag: 'tr', code: 'TR' },
        'vi': { name: 'Vietnamese', flag: 'vn', code: 'VI' },
        'it': { name: 'Italian', flag: 'it', code: 'IT' },
        'th': { name: 'Thai', flag: 'th', code: 'TH' },
        'pl': { name: 'Polish', flag: 'pl', code: 'PL' },
        'uk': { name: 'Ukrainian', flag: 'ua', code: 'UK' },
        'nl': { name: 'Dutch', flag: 'nl', code: 'NL' },
        'ro': { name: 'Romanian', flag: 'ro', code: 'RO' },
        'hu': { name: 'Hungarian', flag: 'hu', code: 'HU' },
        'cs': { name: 'Czech', flag: 'cz', code: 'CS' },
        'sv': { name: 'Swedish', flag: 'se', code: 'SV' },
        'el': { name: 'Greek', flag: 'gr', code: 'EL' },
        'he': { name: 'Hebrew', flag: 'il', code: 'HE' },
        'da': { name: 'Danish', flag: 'dk', code: 'DA' },
        'fi': { name: 'Finnish', flag: 'fi', code: 'FI' },
        'no': { name: 'Norwegian', flag: 'no', code: 'NO' },
        'id': { name: 'Indonesian', flag: 'id', code: 'ID' },
        'ms': { name: 'Malay', flag: 'my', code: 'MS' },
        'tl': { name: 'Filipino', flag: 'ph', code: 'TL' },
        'fa': { name: 'Persian', flag: 'ir', code: 'FA' },
        'sw': { name: 'Swahili', flag: 'ke', code: 'SW' },
        'ta': { name: 'Tamil', flag: 'in', code: 'TA' },
        'te': { name: 'Telugu', flag: 'in', code: 'TE' },
        'mr': { name: 'Marathi', flag: 'in', code: 'MR' },
        'ur': { name: 'Urdu', flag: 'pk', code: 'UR' },
        'gu': { name: 'Gujarati', flag: 'in', code: 'GU' },
        'kn': { name: 'Kannada', flag: 'in', code: 'KN' },
        'ml': { name: 'Malayalam', flag: 'in', code: 'ML' },
        'pa': { name: 'Punjabi', flag: 'in', code: 'PA' },
        'bg': { name: 'Bulgarian', flag: 'bg', code: 'BG' },
        'hr': { name: 'Croatian', flag: 'hr', code: 'HR' },
        'sk': { name: 'Slovak', flag: 'sk', code: 'SK' },
        'lt': { name: 'Lithuanian', flag: 'lt', code: 'LT' },
        'sl': { name: 'Slovenian', flag: 'si', code: 'SL' },
        'lv': { name: 'Latvian', flag: 'lv', code: 'LV' },
        'et': { name: 'Estonian', flag: 'ee', code: 'ET' },
        'sr': { name: 'Serbian', flag: 'rs', code: 'SR' },
        'af': { name: 'Afrikaans', flag: 'za', code: 'AF' },
        'sq': { name: 'Albanian', flag: 'al', code: 'SQ' },
        'hy': { name: 'Armenian', flag: 'am', code: 'HY' },
        'az': { name: 'Azerbaijani', flag: 'az', code: 'AZ' },
        'ka': { name: 'Georgian', flag: 'ge', code: 'KA' },
        'is': { name: 'Icelandic', flag: 'is', code: 'IS' },
        'km': { name: 'Khmer', flag: 'kh', code: 'KM' },
        'lo': { name: 'Lao', flag: 'la', code: 'LO' },
        'mk': { name: 'Macedonian', flag: 'mk', code: 'MK' },
        'mn': { name: 'Mongolian', flag: 'mn', code: 'MN' },
        'ne': { name: 'Nepali', flag: 'np', code: 'NE' },
        'si': { name: 'Sinhala', flag: 'lk', code: 'SI' },
        'zu': { name: 'Zulu', flag: 'za', code: 'ZU' }
    },

    state: {
        currentLanguage: 'en',
        originalContent: new Map(),
        translationsLoaded: {},
        isTranslating: false,
        isInitialized: false
    },

    // Initialize
    async init() {
        console.log('🚀 Initializing Fast Static Translation System...');
        
        const storedLanguage = this.getStoredLanguage();
        this.state.currentLanguage = 'en';
        
        this.storeOriginalContent();
        this.setupEventListeners();
        
        await this.autoTranslateOnLoad();
        
        this.state.isInitialized = true;
        console.log('✅ Translation system ready!');
    },

    // Get stored language
    getStoredLanguage() {
        try {
            return localStorage.getItem(this.config.storageKey) || this.config.defaultLanguage;
        } catch (error) {
            return this.config.defaultLanguage;
        }
    },

    // Store language
    storeLanguage(languageCode) {
        try {
            localStorage.setItem(this.config.storageKey, languageCode);
        } catch (error) {
            console.error('Error storing language:', error);
        }
    },

    // Store original content
    storeOriginalContent() {
        const elements = document.querySelectorAll('[data-translate]');
        elements.forEach((element, index) => {
            const textContent = this.extractTextContent(element.innerHTML);
            if (textContent.trim().length > 0) {
                this.state.originalContent.set(index, {
                    element: element,
                    content: element.innerHTML,
                    textContent: textContent.trim()
                });
            }
        });
    },

    // Extract text content
    extractTextContent(html) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        return tempDiv.textContent || tempDiv.innerText || '';
    },

    // Auto-translate on load
    async autoTranslateOnLoad() {
        const storedLanguage = this.getStoredLanguage();
        
        if (storedLanguage && storedLanguage !== 'en') {
            const language = this.languages[storedLanguage];
            if (language) {
                this.updateLanguageUI(storedLanguage, language.name);
                
                setTimeout(() => {
                    this.translatePage(storedLanguage, language.name, false, true);
                }, 100);
            }
        } else {
            this.updateLanguageUI('en', 'English');
        }
    },

    // Translate page
    async translatePage(languageCode, languageName, shouldStore = true, forceTranslation = false) {
        if (this.state.isTranslating || (languageCode === this.state.currentLanguage && !forceTranslation)) {
            return;
        }

        console.log(`🌍 Translating to: ${languageName}`);

        if (shouldStore) {
            this.storeLanguage(languageCode);
        }

        this.updateLanguageUI(languageCode, languageName);

        try {
            this.state.isTranslating = true;

            if (languageCode === 'en') {
                this.resetToOriginal();
            } else {
                await this.applyStaticTranslations(languageCode);
            }

            this.state.currentLanguage = languageCode;
            console.log(`✅ Translation completed!`);

        } catch (error) {
            console.error(`❌ Translation failed:`, error);
        } finally {
            this.state.isTranslating = false;
        }
    },

    // Apply static translations
    async applyStaticTranslations(targetLanguage) {
        // Try to load from localStorage first
        let translations = AutoStaticTranslationGenerator.loadFromLocalStorage(targetLanguage);
        
        if (!translations) {
            console.log(`⚠️ No cached translations for ${targetLanguage}, generating...`);
            translations = await AutoStaticTranslationGenerator.generateLanguageTranslations(
                targetLanguage, 
                this.languages[targetLanguage].name
            );
            AutoStaticTranslationGenerator.saveToLocalStorage(targetLanguage, translations);
        }

        // Apply translations
        this.state.originalContent.forEach((data) => {
            const originalText = data.textContent;
            if (translations[originalText]) {
                data.element.innerHTML = translations[originalText];
            }
        });
    },

    // Reset to original
    resetToOriginal() {
        this.state.originalContent.forEach((data) => {
            data.element.innerHTML = data.content;
        });
    },

    // Update UI
    updateLanguageUI(languageCode, languageName) {
        const language = this.languages[languageCode];
        if (!language) return;

        const flagElement = document.getElementById('selectedLanguageFlag');
        const textElement = document.getElementById('selectedLanguageText');

        if (flagElement) {
            flagElement.className = `fi fi-${language.flag} flag-icon`;
        }

        if (textElement) {
            textElement.textContent = language.code;
        }

        const dropdown = document.getElementById('languageDropdown');
        if (dropdown) {
            dropdown.querySelectorAll('[data-lang]').forEach(option => {
                option.classList.remove('bg-blue-50', 'text-blue-600', 'font-medium');
            });

            const currentOption = dropdown.querySelector(`[data-lang="${languageCode}"]`);
            if (currentOption) {
                currentOption.classList.add('bg-blue-50', 'text-blue-600', 'font-medium');
            }
        }

        this.closeDropdown();
        document.documentElement.lang = languageCode;
    },

    // Setup event listeners
    setupEventListeners() {
        document.addEventListener('click', (e) => {
            const dropdown = document.getElementById('languageDropdown');
            const trigger = document.getElementById('languageDropdownTrigger');

            if (dropdown && trigger &&
                !trigger.contains(e.target) &&
                !dropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });
    },

    // Toggle dropdown
    toggleDropdown() {
        const dropdown = document.getElementById('languageDropdown');
        const chevron = document.getElementById('languageChevron');

        if (!dropdown) return;

        const isHidden = dropdown.classList.contains('hidden');
        
        if (isHidden) {
            dropdown.classList.remove('hidden');
            if (chevron) chevron.style.transform = 'rotate(180deg)';
        } else {
            dropdown.classList.add('hidden');
            if (chevron) chevron.style.transform = 'rotate(0deg)';
        }
    },

    // Close dropdown
    closeDropdown() {
        const dropdown = document.getElementById('languageDropdown');
        const chevron = document.getElementById('languageChevron');

        if (dropdown && !dropdown.classList.contains('hidden')) {
            dropdown.classList.add('hidden');
            if (chevron) chevron.style.transform = 'rotate(0deg)';
        }
    }
};

// ===== CRITICAL FIX: Global functions now point to FastStaticTranslationSystem =====

window.toggleLanguageDropdown = function() {
    FastStaticTranslationSystem.toggleDropdown();
};

window.selectLanguage = function(languageCode, flagCode, languageName, displayCode) {
    console.log('🔄 selectLanguage called:', languageCode, languageName);
    FastStaticTranslationSystem.translatePage(languageCode, languageName);
};

window.translateToLanguage = function(languageCode, languageName) {
    console.log('🔄 translateToLanguage called:', languageCode, languageName);
    FastStaticTranslationSystem.translatePage(languageCode, languageName);
};

// UTILITY: Generate all translations (run this once)
window.generateAllTranslations = async function() {
    console.log('🎯 Starting translation generation process...');
    console.log('⏱️ This will take approximately 10-15 minutes');
    console.log('📊 Translating to 60+ languages');
    
    const allTranslations = {};

    for (const [code, language] of Object.entries(AutoStaticTranslationGenerator.supportedLanguages)) {
        if (code === 'en') continue;
        
        console.log(`\n--- ${language.name} (${code}) ---`);
        allTranslations[code] = await AutoStaticTranslationGenerator.generateLanguageTranslations(code, language.name);
        AutoStaticTranslationGenerator.saveToLocalStorage(code, allTranslations[code]);
        await AutoStaticTranslationGenerator.delay(1000);
    }
    
    console.log('✅ Generation complete!');
    console.log('💾 All translations saved to localStorage');
    
    return allTranslations;
};

// Initialize on page load
function initializeTranslationSystem() {
    setTimeout(() => {
        if (!FastStaticTranslationSystem.state.isInitialized) {
            FastStaticTranslationSystem.init();
        }
    }, 100);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTranslationSystem);
} else {
    initializeTranslationSystem();
}

console.log('🌍 Fast Static Translation System loaded!');
console.log('💡 To generate translations for all 60+ languages, run: generateAllTranslations()');