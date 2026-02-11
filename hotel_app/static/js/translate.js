// OPTIMIZED TRANSLATION SYSTEM WITH PERSISTENT JSON STORAGE
// This system eliminates redundant API calls by maintaining a persistent translation cache

const OptimizedTranslationSystem = {
    // Persistent translation cache - add new translations here
    translationCache: {
        // Format: 'languageCode': { 'original text': 'translated text' }
        'en': {}, // English (original)
        'zh': {}, // Chinese
        'es': {}, // Spanish
        'hi': {}, // Hindi
        'ar': {}, // Arabic
        'pt': {}, // Portuguese
        'bn': {}, // Bengali
        'ru': {}, // Russian
        'ja': {}, // Japanese
        'de': {}, // German
        'ko': {}, // Korean
        'fr': {}, // French
        'tr': {}, // Turkish
        'vi': {}, // Vietnamese
        'it': {}, // Italian
        'th': {}, // Thai
        'pl': {}, // Polish
        'uk': {}, // Ukrainian
        'nl': {}, // Dutch
        'ro': {}, // Romanian
        'hu': {}, // Hungarian
        'cs': {}, // Czech
        'sv': {}, // Swedish
        'el': {}, // Greek
        'he': {}, // Hebrew
        'da': {}, // Danish
        'fi': {}, // Finnish
        'no': {}, // Norwegian
        'id': {}, // Indonesian
        'ms': {}, // Malay
        'tl': {}, // Filipino
        'fa': {}, // Persian
        'sw': {}, // Swahili
        'ta': {}, // Tamil
        'te': {}, // Telugu
        'mr': {}, // Marathi
        'ur': {}, // Urdu
        'gu': {}, // Gujarati
        'kn': {}, // Kannada
        'ml': {}, // Malayalam
        'pa': {}, // Punjabi
        'bg': {}, // Bulgarian
        'hr': {}, // Croatian
        'sk': {}, // Slovak
        'lt': {}, // Lithuanian
        'sl': {}, // Slovenian
        'lv': {}, // Latvian
        'et': {}, // Estonian
        'sr': {}, // Serbian
        'af': {}, // Afrikaans
        'sq': {}, // Albanian
        'hy': {}, // Armenian
        'az': {}, // Azerbaijani
        'ka': {}, // Georgian
        'is': {}, // Icelandic
        'km': {}, // Khmer
        'lo': {}, // Lao
        'mk': {}, // Macedonian
        'mn': {}, // Mongolian
        'ne': {}, // Nepali
        'si': {}, // Sinhala
        'zu': {}  // Zulu
    },

    // Language configuration
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

    // System state
    state: {
        currentLanguage: 'en',
        originalContent: new Map(),
        isTranslating: false,
        isInitialized: false,
        apiCallCount: 0,
        cacheHitCount: 0
    },

    // Configuration
    config: {
        defaultLanguage: 'en',
        persistLanguage: true,
        storageKey: 'selectedLanguage',
        autoSaveCache: true,
        batchSize: 5,
        delayBetweenBatches: 500
    },

    // Initialize the translation system
    async init() {
        console.log('🚀 Initializing Optimized Translation System...');
        
        // Load saved language preference
        const storedLanguage = this.getStoredLanguage();
        this.state.currentLanguage = 'en';
        
        // Store original content from all data-translate elements
        this.storeOriginalContent();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Auto-translate if needed
        await this.autoTranslateOnLoad();
        
        this.state.isInitialized = true;
        console.log('✅ Translation system ready!');
        console.log(`📊 Cache status: ${this.getCacheStats()}`);
    },

    // Store original content from all elements with data-translate attribute
    storeOriginalContent() {
        const elements = document.querySelectorAll('[data-translate]');
        console.log(`📝 Found ${elements.length} translatable elements`);
        
        elements.forEach((element, index) => {
            const textContent = this.extractTextContent(element);
            if (textContent.trim().length > 0) {
                this.state.originalContent.set(index, {
                    element: element,
                    originalHTML: element.innerHTML,
                    originalText: textContent.trim(),
                    currentText: textContent.trim()
                });
            }
        });
    },

    // Extract clean text content from HTML
    extractTextContent(element) {
        // Clone the element to avoid modifying the original
        const clone = element.cloneNode(true);
        
        // Remove script and style elements
        const scripts = clone.querySelectorAll('script, style');
        scripts.forEach(el => el.remove());
        
        return clone.textContent || clone.innerText || '';
    },

    // Translate a single phrase using API
    async translatePhrase(text, targetLanguage) {
        try {
            this.state.apiCallCount++;
            const url = `https://translate.googleapis.com/translate_a/single?client=gtx&sl=en&tl=${targetLanguage}&dt=t&q=${encodeURIComponent(text)}`;
            const response = await fetch(url);
            const data = await response.json();
            const translated = data[0].map(item => item[0]).join('');
            
            // Save to cache
            this.saveToCache(targetLanguage, text, translated);
            
            return translated;
        } catch (error) {
            console.error(`Translation error for "${text}":`, error);
            return text; // Return original text on error
        }
    },

    // Get translation from cache or API
    async getTranslation(text, targetLanguage) {
        // Check cache first
        if (this.translationCache[targetLanguage] && this.translationCache[targetLanguage][text]) {
            this.state.cacheHitCount++;
            return this.translationCache[targetLanguage][text];
        }
        
        // Not in cache, fetch from API
        return await this.translatePhrase(text, targetLanguage);
    },

    // Save translation to cache
    saveToCache(languageCode, originalText, translatedText) {
        if (!this.translationCache[languageCode]) {
            this.translationCache[languageCode] = {};
        }
        this.translationCache[languageCode][originalText] = translatedText;
        
        if (this.config.autoSaveCache) {
            this.saveCacheToLocalStorage();
        }
    },

    // Save cache to localStorage as backup
    saveCacheToLocalStorage() {
        try {
            localStorage.setItem('translationCache', JSON.stringify(this.translationCache));
        } catch (error) {
            console.error('Error saving cache to localStorage:', error);
        }
    },

    // Load cache from localStorage
    loadCacheFromLocalStorage() {
        try {
            const cached = localStorage.getItem('translationCache');
            if (cached) {
                const loadedCache = JSON.parse(cached);
                // Merge with existing cache
                Object.keys(loadedCache).forEach(lang => {
                    if (!this.translationCache[lang]) {
                        this.translationCache[lang] = {};
                    }
                    this.translationCache[lang] = {
                        ...this.translationCache[lang],
                        ...loadedCache[lang]
                    };
                });
                console.log('✅ Cache loaded from localStorage');
            }
        } catch (error) {
            console.error('Error loading cache from localStorage:', error);
        }
    },

    // Translate entire page
    async translatePage(languageCode, languageName = null, shouldStore = true) {
        if (this.state.isTranslating || languageCode === this.state.currentLanguage) {
            return;
        }

        if (!languageName) {
            languageName = this.languages[languageCode]?.name || languageCode;
        }

        console.log(`🌍 Translating to: ${languageName}`);
        console.log(`📊 Before: API calls: ${this.state.apiCallCount}, Cache hits: ${this.state.cacheHitCount}`);

        if (shouldStore) {
            this.storeLanguage(languageCode);
        }

        this.updateLanguageUI(languageCode, languageName);

        try {
            this.state.isTranslating = true;

            if (languageCode === 'en') {
                // Reset to original English
                this.resetToOriginal();
            } else {
                // Translate to target language
                await this.applyTranslations(languageCode);
            }

            this.state.currentLanguage = languageCode;
            console.log(`✅ Translation completed!`);
            console.log(`📊 After: API calls: ${this.state.apiCallCount}, Cache hits: ${this.state.cacheHitCount}`);

        } catch (error) {
            console.error(`❌ Translation failed:`, error);
        } finally {
            this.state.isTranslating = false;
        }
    },

    // Apply translations to all elements
    async applyTranslations(targetLanguage) {
        const totalElements = this.state.originalContent.size;
        let completed = 0;
        
        // Process in batches to avoid overwhelming the API
        const entries = Array.from(this.state.originalContent.entries());
        
        for (let i = 0; i < entries.length; i += this.config.batchSize) {
            const batch = entries.slice(i, i + this.config.batchSize);
            
            await Promise.all(batch.map(async ([index, data]) => {
                const originalText = data.originalText;
                const translatedText = await this.getTranslation(originalText, targetLanguage);
                
                // Replace text while preserving HTML structure
                this.updateElementText(data.element, originalText, translatedText);
                data.currentText = translatedText;
                
                completed++;
                const progress = Math.round((completed / totalElements) * 100);
                
                if (completed % 10 === 0 || completed === totalElements) {
                    console.log(`  Progress: ${progress}% (${completed}/${totalElements})`);
                }
            }));
            
            // Delay between batches
            if (i + this.config.batchSize < entries.length) {
                await this.delay(this.config.delayBetweenBatches);
            }
        }
    },

    // Update element text while preserving HTML structure
    updateElementText(element, originalText, translatedText) {
        // Simple text node replacement
        if (element.childNodes.length === 1 && element.childNodes[0].nodeType === Node.TEXT_NODE) {
            element.textContent = translatedText;
        } else {
            // More complex: replace text nodes while preserving structure
            this.replaceTextNodes(element, originalText, translatedText);
        }
    },

    // Recursively replace text nodes
    replaceTextNodes(element, originalText, translatedText) {
        const walker = document.createTreeWalker(
            element,
            NodeFilter.SHOW_TEXT,
            null,
            false
        );

        const textNodes = [];
        let node;
        while (node = walker.nextNode()) {
            if (node.textContent.trim().length > 0) {
                textNodes.push(node);
            }
        }

        // Simple replacement for single text node
        if (textNodes.length === 1) {
            textNodes[0].textContent = translatedText;
        } else {
            // For multiple text nodes, replace the first meaningful one
            const mainNode = textNodes.find(n => n.textContent.trim() === originalText);
            if (mainNode) {
                mainNode.textContent = translatedText;
            }
        }
    },

    // Reset to original English content
    resetToOriginal() {
        this.state.originalContent.forEach((data) => {
            data.element.innerHTML = data.originalHTML;
            data.currentText = data.originalText;
        });
    },

    // Auto-translate on page load if needed
    async autoTranslateOnLoad() {
        const storedLanguage = this.getStoredLanguage();
        
        if (storedLanguage && storedLanguage !== 'en') {
            const language = this.languages[storedLanguage];
            if (language) {
                this.updateLanguageUI(storedLanguage, language.name);
                
                setTimeout(() => {
                    this.translatePage(storedLanguage, language.name, false);
                }, 100);
            }
        } else {
            this.updateLanguageUI('en', 'English');
        }
    },

    // Get stored language preference
    getStoredLanguage() {
        try {
            return localStorage.getItem(this.config.storageKey) || this.config.defaultLanguage;
        } catch (error) {
            return this.config.defaultLanguage;
        }
    },

    // Store language preference
    storeLanguage(languageCode) {
        try {
            localStorage.setItem(this.config.storageKey, languageCode);
        } catch (error) {
            console.error('Error storing language:', error);
        }
    },

    // Update language UI
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

        // Update dropdown selection
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
        // Close dropdown when clicking outside
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
    },

    // Helper: delay function
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    },

    // Get cache statistics
    getCacheStats() {
        let totalTranslations = 0;
        Object.keys(this.translationCache).forEach(lang => {
            totalTranslations += Object.keys(this.translationCache[lang]).length;
        });
        return `${totalTranslations} translations cached across ${Object.keys(this.translationCache).length} languages`;
    },

    // Export cache as JSON for permanent storage
    exportCacheAsJSON() {
        const json = JSON.stringify(this.translationCache, null, 2);
        console.log('📦 Translation Cache JSON:');
        console.log(json);
        
        // Download as file
        const blob = new Blob([json], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'translation-cache.json';
        a.click();
        URL.revokeObjectURL(url);
        
        return json;
    },

    // Import cache from JSON
    importCacheFromJSON(jsonData) {
        try {
            const imported = typeof jsonData === 'string' ? JSON.parse(jsonData) : jsonData;
            
            Object.keys(imported).forEach(lang => {
                if (!this.translationCache[lang]) {
                    this.translationCache[lang] = {};
                }
                this.translationCache[lang] = {
                    ...this.translationCache[lang],
                    ...imported[lang]
                };
            });
            
            this.saveCacheToLocalStorage();
            console.log('✅ Cache imported successfully');
            console.log(`📊 ${this.getCacheStats()}`);
        } catch (error) {
            console.error('Error importing cache:', error);
        }
    }
};

// ===== GLOBAL INTERFACE FUNCTIONS =====

window.toggleLanguageDropdown = function() {
    OptimizedTranslationSystem.toggleDropdown();
};

window.selectLanguage = function(languageCode, flagCode, languageName, displayCode) {
    console.log('🔄 Changing language to:', languageName);
    OptimizedTranslationSystem.translatePage(languageCode, languageName);
};

window.translateToLanguage = function(languageCode, languageName) {
    console.log('🔄 Translating to:', languageName);
    OptimizedTranslationSystem.translatePage(languageCode, languageName);
};

// ===== UTILITY FUNCTIONS =====

// Export current cache
window.exportTranslationCache = function() {
    return OptimizedTranslationSystem.exportCacheAsJSON();
};

// Import cache from JSON
window.importTranslationCache = function(jsonData) {
    OptimizedTranslationSystem.importCacheFromJSON(jsonData);
};

// Get cache statistics
window.getTranslationStats = function() {
    console.log('📊 Translation Statistics:');
    console.log(`  Current Language: ${OptimizedTranslationSystem.state.currentLanguage}`);
    console.log(`  API Calls Made: ${OptimizedTranslationSystem.state.apiCallCount}`);
    console.log(`  Cache Hits: ${OptimizedTranslationSystem.state.cacheHitCount}`);
    console.log(`  Cache Efficiency: ${OptimizedTranslationSystem.state.cacheHitCount > 0 
        ? Math.round((OptimizedTranslationSystem.state.cacheHitCount / (OptimizedTranslationSystem.state.apiCallCount + OptimizedTranslationSystem.state.cacheHitCount)) * 100) 
        : 0}%`);
    console.log(`  ${OptimizedTranslationSystem.getCacheStats()}`);
};

// Clear all cache
window.clearTranslationCache = function() {
    if (confirm('Are you sure you want to clear all translation cache?')) {
        OptimizedTranslationSystem.translationCache = {};
        Object.keys(OptimizedTranslationSystem.languages).forEach(lang => {
            OptimizedTranslationSystem.translationCache[lang] = {};
        });
        OptimizedTranslationSystem.saveCacheToLocalStorage();
        console.log('🗑️ Translation cache cleared');
    }
};

// Pre-translate all content for a language
window.preTranslateLanguage = async function(languageCode) {
    const language = OptimizedTranslationSystem.languages[languageCode];
    if (!language) {
        console.error('Invalid language code');
        return;
    }
    
    console.log(`🔄 Pre-translating all content for ${language.name}...`);
    
    const allTexts = Array.from(OptimizedTranslationSystem.state.originalContent.values())
        .map(data => data.originalText);
    
    const uniqueTexts = [...new Set(allTexts)];
    console.log(`📝 Found ${uniqueTexts.length} unique phrases to translate`);
    
    let translated = 0;
    for (const text of uniqueTexts) {
        await OptimizedTranslationSystem.getTranslation(text, languageCode);
        translated++;
        if (translated % 10 === 0) {
            console.log(`  Progress: ${Math.round((translated / uniqueTexts.length) * 100)}%`);
        }
        await OptimizedTranslationSystem.delay(300);
    }
    
    console.log(`✅ Pre-translation complete for ${language.name}`);
    console.log(`📦 Export cache with: exportTranslationCache()`);
};

// ===== AUTO-INITIALIZATION =====

function initializeTranslationSystem() {
    // Load cache from localStorage first
    OptimizedTranslationSystem.loadCacheFromLocalStorage();
    
    // Initialize the system
    setTimeout(() => {
        if (!OptimizedTranslationSystem.state.isInitialized) {
            OptimizedTranslationSystem.init();
        }
    }, 100);
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeTranslationSystem);
} else {
    initializeTranslationSystem();
}

// console.log('🌍 Optimized Translation System Loaded!');
// console.log('💡 Useful commands:');
// console.log('  - getTranslationStats() - View translation statistics');
// console.log('  - exportTranslationCache() - Export cache as JSON file');
// console.log('  - importTranslationCache(json) - Import cache from JSON');
// console.log('  - preTranslateLanguage("es") - Pre-translate all content for a language');
// console.log('  - clearTranslationCache() - Clear all cached translations');