// Enhanced Translation System with Dropdown Support
const TranslationSystem = {
    // Configuration optimized for speed
    config: {
        apiEndpoints: [
            'https://api.mymemory.translated.net/get', // MyMemory API (has CORS)
            'https://libretranslate.de/translate',
            'https://translate.argosopentech.com/translate'
        ],
        defaultLanguage: 'en',
        timeout: 5000,
        maxRetries: 0,
        batchSize: 10,
        maxConcurrent: 5,
        useCache: true,
        preloadTranslations: true,
        instantSwitch: true
    },

    // Language configuration with flag mapping
    languages: {
        'en': { name: 'English', flag: 'us', code: 'EN' },
        'pt': { name: 'Português', flag: 'pt', code: 'PT' },
        'es': { name: 'Español', flag: 'es', code: 'ES' },
        'it': { name: 'Italiano', flag: 'it', code: 'IT' },
        'fr': { name: 'Français', flag: 'fr', code: 'FR' },
        'de': { name: 'Deutsch', flag: 'de', code: 'DE' }
    },

    // State management with caching and preloading
    state: {
        currentLanguage: 'en',
        originalContent: new Map(),
        translationCache: new Map(),
        isTranslating: false,
        debugMode: true,
        preloadedLanguages: new Set(['en']),
        translatedContent: new Map(),
        semaphore: 0,
        isDropdownOpen: false
    },

    // Initialize the system
    init() {
        this.log('Initializing translation system with dropdown...');
        this.storeOriginalContent();
        this.setupDropdownEventListeners();
        this.preloadCommonTranslations();
        this.log('Translation system ready!');
    },

    // Setup dropdown event listeners
    setupDropdownEventListeners() {
        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            const dropdown = document.getElementById('languageDropdown');
            const trigger = e.target.closest('[onclick*="toggleLanguageDropdown"]');

            if (dropdown && !trigger && !dropdown.contains(e.target)) {
                this.closeDropdown();
            }
        });

        // Setup online/offline listeners
        window.addEventListener('online', () => {
            this.hideError();
            this.log('Connection restored');
        });

        window.addEventListener('offline', () => {
            this.showError('You are offline. Translation services are not available.');
            this.log('Connection lost');
        });
    },

    // Preload common translations for instant switching
    async preloadCommonTranslations() {
        if (!this.config.preloadTranslations) return;

        this.log('Preloading translations for instant switching...');
        const commonLanguages = ['es', 'fr', 'de', 'pt', 'it'];

        // Background preload API translations for better quality
        setTimeout(() => this.backgroundPreloadAPITranslations(commonLanguages), 2000);
    },

    // Background API preloading (non-blocking)
    async backgroundPreloadAPITranslations(languages) {
        this.log('Starting background API preloading...');

        for (const lang of languages) {
            try {
                await this.preloadLanguageViaAPI(lang);
            } catch (error) {
                this.log(`Background preload failed for ${lang}: ${error.message}`);
            }
        }
    },

    // Preload specific language via API
    async preloadLanguageViaAPI(targetLanguage) {
        const elements = Array.from(this.state.originalContent.values());
        const translatedContent = new Map();

        // Process in smaller batches to avoid overwhelming the API
        for (let i = 0; i < elements.length; i += 2) {
            const batch = elements.slice(i, i + 2);

            await Promise.all(batch.map(async (data, batchIndex) => {
                const globalIndex = i + batchIndex;
                try {
                    const translatedText = await this.translateText(
                        data.textContent,
                        'en',
                        targetLanguage
                    );
                    translatedContent.set(globalIndex, translatedText);
                } catch (error) {
                    // Silently fail for background preloading
                }
            }));

            // Small delay to be respectful to APIs
            await this.delay(500);
        }

        if (translatedContent.size > 0) {
            this.state.translatedContent.set(targetLanguage, translatedContent);
            this.state.preloadedLanguages.add(targetLanguage);
            this.log(`Background preloaded ${translatedContent.size} API translations for ${targetLanguage}`);
        }
    },

    // Debug logging
    log(message, type = 'info') {
        if (this.state.debugMode) {
            // console.log(`[Translation] ${message}`);
        }
    },

    // Store original content
    storeOriginalContent() {
        const elements = document.querySelectorAll('[data-translate]');
        elements.forEach((element, index) => {
            this.state.originalContent.set(index, {
                element: element,
                content: element.innerHTML,
                textContent: this.extractTextContent(element.innerHTML)
            });
        });
        this.log(`Stored ${elements.length} translatable elements`);
    },

    // Extract clean text content from HTML
    extractTextContent(html) {
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        return tempDiv.textContent || tempDiv.innerText || '';
    },

    // Toggle dropdown function
    toggleDropdown() {
        const dropdown = document.getElementById('languageDropdown');
        const chevron = document.getElementById('languageChevron');

        if (!dropdown || !chevron) return;

        this.state.isDropdownOpen = !this.state.isDropdownOpen;

        if (this.state.isDropdownOpen) {
            dropdown.classList.remove('hidden');
            chevron.style.transform = 'rotate(180deg)';
        } else {
            dropdown.classList.add('hidden');
            chevron.style.transform = 'rotate(0deg)';
        }
    },

    // Close dropdown
    closeDropdown() {
        const dropdown = document.getElementById('languageDropdown');
        const chevron = document.getElementById('languageChevron');

        if (!dropdown || !chevron) return;

        dropdown.classList.add('hidden');
        chevron.style.transform = 'rotate(0deg)';
        this.state.isDropdownOpen = false;
    },

    // Update language selection UI
    updateLanguageUI(languageCode, languageName) {
        const language = this.languages[languageCode];
        if (!language) return;

        // Update selected language display
        const flagElement = document.getElementById('selectedLanguageFlag');
        const textElement = document.getElementById('selectedLanguageText');

        if (flagElement && textElement) {
            flagElement.className = `fi fi-${language.flag} flag-icon`;
            textElement.textContent = language.code;
        }

        // Update dropdown options - remove active state from all, add to current
        const dropdown = document.getElementById('languageDropdown');
        if (dropdown) {
            // Remove active state from all options
            dropdown.querySelectorAll('[onclick*="selectLanguage"], [onclick*="translateToLanguage"]').forEach(option => {
                option.classList.remove('bg-blue-50', 'text-blue-600', 'font-medium');
            });

            // Add active state to current language
            const currentOption = dropdown.querySelector(`[data-lang="${languageCode}"]`) ||
                dropdown.querySelector(`[onclick*="'${languageCode}'"]`);
            if (currentOption) {
                currentOption.classList.add('bg-blue-50', 'text-blue-600', 'font-medium');
            }
        }

        // Close dropdown after selection
        this.closeDropdown();

        // Update document language
        document.documentElement.lang = languageCode;
        this.state.currentLanguage = languageCode;
    },

    // Main translation function
    async translatePage(languageCode, languageName) {
        if (this.state.isTranslating || languageCode === this.state.currentLanguage) {
            return;
        }

        this.log(`Starting translation to ${languageCode} (${languageName})`);

        // Update UI immediately
        this.updateLanguageUI(languageCode, languageName);

        // Instant switch for preloaded content
        if (this.config.instantSwitch && this.state.preloadedLanguages.has(languageCode)) {
            this.log(`Using preloaded translations for instant switch to ${languageName}`);
            this.instantSwitchToLanguage(languageCode, languageName);
            return;
        }

        try {
            this.setTranslatingState(true);

            if (languageCode === 'en') {
                await this.resetToOriginal();
            } else {
                await this.translateContentFast(languageCode);
            }

            this.showSuccess(`Successfully translated to ${languageName}!`);
            this.log(`Translation to ${languageName} completed`);

        } catch (error) {
            this.log(`Translation failed: ${error.message}`, 'error');
            this.showError(`Translation failed: ${error.message}`);
        } finally {
            this.setTranslatingState(false);
        }
    },

    // Instant language switching for preloaded content
    instantSwitchToLanguage(targetLanguage, languageName) {
        const translatedContent = this.state.translatedContent.get(targetLanguage);

        if (translatedContent) {
            // Apply translations instantly
            this.state.originalContent.forEach((data, index) => {
                if (translatedContent.has(index)) {
                    data.element.innerHTML = translatedContent.get(index);
                }
            });

            this.showSuccess(`Instantly switched to ${languageName}!`);
            this.log(`Instant switch to ${languageName} completed`);
        }
    },

    // Reset content to original English
    async resetToOriginal() {
        this.state.originalContent.forEach((data, index) => {
            data.element.innerHTML = data.content;
        });
        await this.delay(300);
    },

    // High-speed translation with parallel processing
    async translateContentFast(targetLanguage) {
        const elements = Array.from(this.state.originalContent.values());
        const totalElements = elements.length;

        this.log(`Fast translating ${totalElements} elements to ${targetLanguage}`);

        // Check if we have cached translations first
        const cachedContent = this.state.translatedContent.get(targetLanguage);
        if (cachedContent) {
            this.log(`Using cached translations for ${targetLanguage}`);
            cachedContent.forEach((translatedText, index) => {
                const data = this.state.originalContent.get(index);
                if (data) {
                    data.element.innerHTML = translatedText;
                }
            });
            return;
        }

        // Parallel processing with concurrency control
        const chunks = this.chunkArray(elements, this.config.batchSize);

        for (let chunkIndex = 0; chunkIndex < chunks.length; chunkIndex++) {
            const chunk = chunks[chunkIndex];
            await this.processChunkWithSemaphore(chunk, targetLanguage, chunkIndex * this.config.batchSize);
        }

        // Cache the results for next time
        const translatedContent = new Map();
        this.state.originalContent.forEach((data, index) => {
            const currentContent = data.element.innerHTML;
            if (currentContent !== data.content) {
                translatedContent.set(index, currentContent);
            }
        });

        if (translatedContent.size > 0) {
            this.state.translatedContent.set(targetLanguage, translatedContent);
            this.state.preloadedLanguages.add(targetLanguage);
            this.log(`Cached ${translatedContent.size} translations for future use`);
        }
    },

    // Process chunk with semaphore for concurrency control
    async processChunkWithSemaphore(chunk, targetLanguage, startIndex) {
        const promises = chunk.map(async (data, chunkIndex) => {
            const globalIndex = startIndex + chunkIndex;

            // Wait for semaphore
            while (this.state.semaphore >= this.config.maxConcurrent) {
                await this.delay(10);
            }

            this.state.semaphore++;

            try {
                const translatedText = await Promise.race([
                    this.translateText(data.textContent, 'en', targetLanguage),
                    this.delay(this.config.timeout).then(() => { throw new Error('Timeout'); })
                ]);

                if (translatedText && translatedText !== data.textContent) {
                    data.element.innerHTML = translatedText;
                }

            } catch (error) {
                this.log(`Failed to translate element ${globalIndex}: ${error.message}`, 'error');
            } finally {
                this.state.semaphore--;
            }
        });

        await Promise.all(promises);
    },

    // Utility function to chunk arrays
    chunkArray(array, chunkSize) {
        const chunks = [];
        for (let i = 0; i < array.length; i += chunkSize) {
            chunks.push(array.slice(i, i + chunkSize));
        }
        return chunks;
    },

    // Translate individual text using MyMemory API
    async translateText(text, sourceLanguage, targetLanguage) {
        const cacheKey = `${sourceLanguage}-${targetLanguage}-${text.substring(0, 50)}`;
        if (this.state.translationCache.has(cacheKey)) {
            return this.state.translationCache.get(cacheKey);
        }

        // Try MyMemory API first (has CORS support)
        try {
            const myMemoryUrl = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${sourceLanguage}|${targetLanguage}`;

            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);

            const response = await fetch(myMemoryUrl, {
                method: 'GET',
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            if (response.ok) {
                const data = await response.json();
                if (data.responseData && data.responseData.translatedText) {
                    const translatedText = data.responseData.translatedText;
                    this.state.translationCache.set(cacheKey, translatedText);
                    this.log(`MyMemory API translation successful`);
                    return translatedText;
                }
            }
        } catch (error) {
            this.log(`MyMemory API failed: ${error.message}`, 'error');
        }

        throw new Error('Translation API failed or blocked by CORS');
    },

    // UI Helper Methods
    setTranslatingState(isTranslating) {
        this.state.isTranslating = isTranslating;

        // Disable dropdown during translation
        const dropdownTrigger = document.querySelector('[onclick*="toggleLanguageDropdown"]');
        if (dropdownTrigger) {
            dropdownTrigger.style.pointerEvents = isTranslating ? 'none' : 'auto';
            dropdownTrigger.style.opacity = isTranslating ? '0.5' : '1';
        }
    },

    showError(message) {
        // console.error('[Translation Error]', message);
        // You can implement custom error display here
    },

    showSuccess(message) {
        // console.log('[Translation Success]', message);
        // You can implement custom success display here
    },

    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
};

// Global functions for dropdown interaction
function toggleLanguageDropdown() {
    TranslationSystem.toggleDropdown();
}

function selectLanguage(languageCode, flagCode, languageName, displayCode) {
    if (languageCode === 'en') {
        TranslationSystem.translatePage('en', 'English');
    } else {
        TranslationSystem.translatePage(languageCode, languageName);
    }
}

function translateToLanguage(languageCode, languageName) {
    TranslationSystem.translatePage(languageCode, languageName);
}

// Initialize the translation system when page loads
document.addEventListener('DOMContentLoaded', function () {
    TranslationSystem.init();
});