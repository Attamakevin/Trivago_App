 // Enhanced Translation System with Speed Optimizations
        const TranslationSystem = {
            // Configuration optimized for speed
            config: {
                apiEndpoints: [
                    'https://api.mymemory.translated.net/get', // MyMemory API (has CORS)
                    'https://libretranslate.de/translate',
                    'https://translate.argosopentech.com/translate'
                ],
                defaultLanguage: 'en',
                timeout: 5000, // Reduced timeout for faster failures
                maxRetries: 0, // No retries for speed
                batchSize: 10, // Larger batches for parallel processing
                maxConcurrent: 5, // Limit concurrent requests to avoid rate limiting
                useCache: true,
                preloadTranslations: true,
                instantSwitch: true // Enable instant switching for cached content
            },
            
            // Enhanced static translations for instant switching
            staticTranslations: {
                'es': {
                    'Welcome to Our Global Website': 'Bienvenido a Nuestro Sitio Web Global',
                    'Experience our content in your preferred language using free translation technology': 'Experimenta nuestro contenido en tu idioma preferido usando tecnología de traducción gratuita',
                    'About Our Company': 'Acerca de Nuestra Empresa',
                    'We are a leading technology company providing innovative solutions to businesses worldwide. Our mission is to bridge language barriers and connect people across different cultures through advanced translation technology.': 'Somos una empresa de tecnología líder que brinda soluciones innovadoras a empresas de todo el mundo. Nuestra misión es eliminar las barreras del idioma y conectar a las personas de diferentes culturas a través de tecnología de traducción avanzada.',
                    'Our Services': 'Nuestros Servicios',
                    'Professional web development and design': 'Desarrollo y diseño web profesional',
                    'Multi-language website solutions': 'Soluciones de sitios web multiidioma',
                    'E-commerce platform development': 'Desarrollo de plataformas de comercio electrónico',
                    'Mobile application development': 'Desarrollo de aplicaciones móviles',
                    'Digital marketing and SEO services': 'Marketing digital y servicios de SEO',
                    '24/7 customer support in multiple languages': 'Soporte al cliente 24/7 en múltiples idiomas',
                    'Why Choose Us?': '¿Por Qué Elegirnos?',
                    'With over 15 years of experience in the technology industry, we have successfully delivered projects for clients in more than 50 countries. Our team of expert developers and designers are committed to delivering high-quality solutions that exceed expectations.': 'Con más de 15 años de experiencia en la industria tecnológica, hemos entregado exitosamente proyectos para clientes en más de 50 países. Nuestro equipo de desarrolladores y diseñadores expertos se compromete a entregar soluciones de alta calidad que superen las expectativas.',
                    'We believe in the power of communication and strive to make our services accessible to everyone, regardless of their native language. That\'s why we\'ve integrated free translation technology into our website.': 'Creemos en el poder de la comunicación y nos esforzamos por hacer nuestros servicios accesibles para todos, sin importar su idioma nativo. Por eso hemos integrado tecnología de traducción gratuita en nuestro sitio web.',
                    'Contact Information': 'Información de Contacto',
                    'Translation Technology': 'Tecnología de Traducción',
                    'This demo uses a fallback translation system with detailed error reporting to help diagnose connection issues with LibreTranslate APIs.': 'Esta demostración utiliza un sistema de traducción de respaldo con informes de errores detallados para ayudar a diagnosticar problemas de conexión con las APIs de LibreTranslate.',
                    'In a production environment, you would need to set up your own LibreTranslate instance or use a backend proxy service.': 'En un entorno de producción, necesitarías configurar tu propia instancia de LibreTranslate o usar un servicio proxy de backend.',
                    '© 2025 Your Company Name. All rights reserved.': '© 2025 Nombre de Tu Empresa. Todos los derechos reservados.',
                    'Powered by Translation Technology': 'Impulsado por Tecnología de Traducción'
                },
                'fr': {
                    'Welcome to Our Global Website': 'Bienvenue sur Notre Site Web Global',
                    'Experience our content in your preferred language using free translation technology': 'Découvrez notre contenu dans votre langue préférée en utilisant une technologie de traduction gratuite',
                    'About Our Company': 'À Propos de Notre Entreprise',
                    'We are a leading technology company providing innovative solutions to businesses worldwide. Our mission is to bridge language barriers and connect people across different cultures through advanced translation technology.': 'Nous sommes une entreprise technologique de premier plan fournissant des solutions innovantes aux entreprises du monde entier. Notre mission est de surmonter les barrières linguistiques et de connecter les personnes de différentes cultures grâce à une technologie de traduction avancée.',
                    'Our Services': 'Nos Services',
                    'Professional web development and design': 'Développement et conception web professionnels',
                    'Multi-language website solutions': 'Solutions de sites web multilingues',
                    'E-commerce platform development': 'Développement de plateformes e-commerce',
                    'Mobile application development': 'Développement d\'applications mobiles',
                    'Digital marketing and SEO services': 'Marketing digital et services SEO',
                    '24/7 customer support in multiple languages': 'Support client 24/7 en plusieurs langues',
                    'Why Choose Us?': 'Pourquoi Nous Choisir?',
                    'With over 15 years of experience in the technology industry, we have successfully delivered projects for clients in more than 50 countries. Our team of expert developers and designers are committed to delivering high-quality solutions that exceed expectations.': 'Avec plus de 15 ans d\'expérience dans l\'industrie technologique, nous avons livré avec succès des projets pour des clients dans plus de 50 pays. Notre équipe de développeurs et designers experts s\'engage à fournir des solutions de haute qualité qui dépassent les attentes.',
                    'We believe in the power of communication and strive to make our services accessible to everyone, regardless of their native language. That\'s why we\'ve integrated free translation technology into our website.': 'Nous croyons au pouvoir de la communication et nous nous efforçons de rendre nos services accessibles à tous, indépendamment de leur langue maternelle. C\'est pourquoi nous avons intégré une technologie de traduction gratuite dans notre site web.',
                    'Contact Information': 'Informations de Contact',
                    'Translation Technology': 'Technologie de Traduction',
                    'This demo uses a fallback translation system with detailed error reporting to help diagnose connection issues with LibreTranslate APIs.': 'Cette démo utilise un système de traduction de secours avec des rapports d\'erreurs détaillés pour aider à diagnostiquer les problèmes de connexion avec les APIs LibreTranslate.',
                    'In a production environment, you would need to set up your own LibreTranslate instance or use a backend proxy service.': 'Dans un environnement de production, vous devriez configurer votre propre instance LibreTranslate ou utiliser un service proxy backend.',
                    '© 2025 Your Company Name. All rights reserved.': '© 2025 Nom de Votre Entreprise. Tous droits réservés.',
                    'Powered by Translation Technology': 'Alimenté par la Technologie de Traduction'
                },
                'de': {
                    'Welcome to Our Global Website': 'Willkommen auf Unserer Globalen Website',
                    'Experience our content in your preferred language using free translation technology': 'Erleben Sie unsere Inhalte in Ihrer bevorzugten Sprache mit kostenloser Übersetzungstechnologie',
                    'About Our Company': 'Über Unser Unternehmen',
                    'We are a leading technology company providing innovative solutions to businesses worldwide. Our mission is to bridge language barriers and connect people across different cultures through advanced translation technology.': 'Wir sind ein führendes Technologieunternehmen, das innovative Lösungen für Unternehmen weltweit bereitstellt. Unsere Mission ist es, Sprachbarrieren zu überwinden und Menschen verschiedener Kulturen durch fortschrittliche Übersetzungstechnologie zu verbinden.',
                    'Our Services': 'Unsere Dienstleistungen',
                    'Professional web development and design': 'Professionelle Webentwicklung und -design',
                    'Multi-language website solutions': 'Mehrsprachige Website-Lösungen',
                    'E-commerce platform development': 'E-Commerce-Plattform-Entwicklung',
                    'Mobile application development': 'Mobile Anwendungsentwicklung',
                    'Digital marketing and SEO services': 'Digitales Marketing und SEO-Services',
                    '24/7 customer support in multiple languages': '24/7 Kundensupport in mehreren Sprachen',
                    'Why Choose Us?': 'Warum Uns Wählen?',
                    'With over 15 years of experience in the technology industry, we have successfully delivered projects for clients in more than 50 countries. Our team of expert developers and designers are committed to delivering high-quality solutions that exceed expectations.': 'Mit über 15 Jahren Erfahrung in der Technologiebranche haben wir erfolgreich Projekte für Kunden in mehr als 50 Ländern geliefert. Unser Team aus erfahrenen Entwicklern und Designern ist bestrebt, hochwertige Lösungen zu liefern, die Erwartungen übertreffen.',
                    'We believe in the power of communication and strive to make our services accessible to everyone, regardless of their native language. That\'s why we\'ve integrated free translation technology into our website.': 'Wir glauben an die Macht der Kommunikation und bemühen uns, unsere Dienstleistungen für alle zugänglich zu machen, unabhängig von ihrer Muttersprache. Deshalb haben wir kostenlose Übersetzungstechnologie in unsere Website integriert.',
                    'Contact Information': 'Kontaktinformationen',
                    'Translation Technology': 'Übersetzungstechnologie',
                    'This demo uses a fallback translation system with detailed error reporting to help diagnose connection issues with LibreTranslate APIs.': 'Diese Demo verwendet ein Fallback-Übersetzungssystem mit detaillierter Fehlerberichterstattung, um Verbindungsprobleme mit LibreTranslate-APIs zu diagnostizieren.',
                    'In a production environment, you would need to set up your own LibreTranslate instance or use a backend proxy service.': 'In einer Produktionsumgebung müssten Sie Ihre eigene LibreTranslate-Instanz einrichten oder einen Backend-Proxy-Service verwenden.',
                    '© 2025 Your Company Name. All rights reserved.': '© 2025 Ihr Firmenname. Alle Rechte vorbehalten.',
                    'Powered by Translation Technology': 'Angetrieben von Übersetzungstechnologie'
                }
            },
            
            // State management with caching and preloading
            state: {
                currentLanguage: 'en',
                originalContent: new Map(),
                translationCache: new Map(),
                isTranslating: false,
                debugMode: true,
                preloadedLanguages: new Set(['en']),
                translatedContent: new Map(), // Store translated HTML for instant switching
                semaphore: 0 // For limiting concurrent requests
            },
            
            // Initialize the system with preloading
            init() {
                this.log('Initializing high-speed translation system...');
                this.storeOriginalContent();
                this.setupEventListeners();
                this.preloadCommonTranslations();
                this.log('Translation system ready!');
            },
            
            // Preload common translations for instant switching
            async preloadCommonTranslations() {
                if (!this.config.preloadTranslations) return;
                
                this.log('Preloading translations for instant switching...');
                const commonLanguages = ['es', 'fr', 'de'];
                
                // Use static translations for instant preloading
                for (const lang of commonLanguages) {
                    if (this.staticTranslations[lang]) {
                        const translatedContent = new Map();
                        
                        this.state.originalContent.forEach((data, index) => {
                            const staticTranslation = this.getStaticTranslation(data.textContent, lang);
                            if (staticTranslation !== data.textContent) {
                                translatedContent.set(index, staticTranslation);
                            }
                        });
                        
                        if (translatedContent.size > 0) {
                            this.state.translatedContent.set(lang, translatedContent);
                            this.state.preloadedLanguages.add(lang);
                            this.log(`Preloaded ${translatedContent.size} translations for ${lang}`);
                        }
                    }
                }
                
                // Background preload API translations for better quality
                setTimeout(() => this.backgroundPreloadAPITranslations(), 2000);
            },
            
            // Background API preloading (non-blocking)
            async backgroundPreloadAPITranslations() {
                this.log('Starting background API preloading...');
                const languages = ['es', 'fr', 'de'];
                
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
                    console.log(`[Translation] ${message}`);
                    const debugEl = document.getElementById('debug-info');
                    if (debugEl) {
                        const timestamp = new Date().toLocaleTimeString();
                        debugEl.innerHTML += `[${timestamp}] ${message}<br>`;
                        debugEl.scrollTop = debugEl.scrollHeight;
                    }
                }
            },
            
            // Store original content
            storeOriginalContent() {
                const elements = document.querySelectorAll('.translatable');
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
            
            // Setup event listeners
            setupEventListeners() {
                window.addEventListener('online', () => {
                    this.hideError();
                    this.log('Connection restored');
                });
                
                window.addEventListener('offline', () => {
                    this.showError('You are offline. Translation services are not available.');
                    this.log('Connection lost');
                });
            },
            
            // Ultra-fast translation function with instant switching
            async translatePage(targetLanguage, languageName) {
                if (this.state.isTranslating || targetLanguage === this.state.currentLanguage) {
                    return;
                }
                
                this.log(`Starting translation to ${targetLanguage} (${languageName})`);
                
                // Instant switch for preloaded content
                if (this.config.instantSwitch && this.state.preloadedLanguages.has(targetLanguage)) {
                    this.log(`Using preloaded translations for instant switch to ${languageName}`);
                    this.instantSwitchToLanguage(targetLanguage, languageName);
                    return;
                }
                
                try {
                    this.setTranslatingState(true);
                    this.showProgress(true);
                    this.updateProgress(0, `Preparing translation to ${languageName}...`);
                    
                    if (targetLanguage === 'en') {
                        await this.resetToOriginal();
                    } else {
                        await this.translateContentFast(targetLanguage);
                    }
                    
                    this.updateLanguageState(targetLanguage, languageName);
                    this.showSuccess(`Successfully translated to ${languageName}!`);
                    this.log(`Translation to ${languageName} completed`);
                    
                } catch (error) {
                    this.log(`Translation failed: ${error.message}`, 'error');
                    this.showError(`Translation failed: ${error.message}`);
                } finally {
                    this.setTranslatingState(false);
                    this.showProgress(false);
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
                    
                    this.updateLanguageState(targetLanguage, languageName);
                    this.showSuccess(`Instantly switched to ${languageName}!`);
                    this.log(`Instant switch to ${languageName} completed`);
                }
            },
            
            // Reset content to original English
            async resetToOriginal() {
                this.updateProgress(50, 'Restoring original content...');
                
                this.state.originalContent.forEach((data, index) => {
                    data.element.innerHTML = data.content;
                });
                
                await this.delay(300);
                this.updateProgress(100, 'Content restored!');
            },
            
            // High-speed translation with parallel processing
            async translateContentFast(targetLanguage) {
                const elements = Array.from(this.state.originalContent.values());
                const totalElements = elements.length;
                let processedElements = 0;
                
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
                    this.updateProgress(100, 'Applied cached translations!');
                    return;
                }
                
                // Parallel processing with concurrency control
                const semaphore = this.config.maxConcurrent;
                const chunks = this.chunkArray(elements, this.config.batchSize);
                
                for (let chunkIndex = 0; chunkIndex < chunks.length; chunkIndex++) {
                    const chunk = chunks[chunkIndex];
                    
                    // Process chunk with concurrency limit
                    await this.processChunkWithSemaphore(chunk, targetLanguage, chunkIndex * this.config.batchSize);
                    
                    processedElements += chunk.length;
                    const progress = Math.floor((processedElements / totalElements) * 100);
                    this.updateProgress(progress, `Fast translating... (${processedElements}/${totalElements})`);
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
                        // Try static translation first (instant)
                        let translatedText = this.getStaticTranslation(data.textContent, targetLanguage);
                        
                        // If no static translation, try API (with timeout)
                        if (translatedText === data.textContent) {
                            try {
                                translatedText = await Promise.race([
                                    this.translateText(data.textContent, 'en', targetLanguage),
                                    this.delay(this.config.timeout).then(() => { throw new Error('Timeout'); })
                                ]);
                            } catch (apiError) {
                                // Keep static translation or original
                                this.log(`API failed for element ${globalIndex}, using fallback`);
                            }
                        }
                        
                        // Update element if we have a translation
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
            
            // Get static translation (fallback)
            getStaticTranslation(text, targetLanguage) {
                if (this.staticTranslations[targetLanguage] && this.staticTranslations[targetLanguage][text]) {
                    return this.staticTranslations[targetLanguage][text];
                }
                return text; // Return original if no translation available
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
                
                // If MyMemory fails, try LibreTranslate APIs
                for (let i = 1; i < this.config.apiEndpoints.length; i++) {
                    const endpoint = this.config.apiEndpoints[i];
                    
                    try {
                        const requestData = {
                            q: text,
                            source: sourceLanguage,
                            target: targetLanguage,
                            format: 'text'
                        };
                        
                        const controller = new AbortController();
                        const timeoutId = setTimeout(() => controller.abort(), this.config.timeout);
                        
                        const response = await fetch(endpoint, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                            },
                            body: JSON.stringify(requestData),
                            signal: controller.signal
                        });
                        
                        clearTimeout(timeoutId);
                        
                        if (response.ok) {
                            const data = await response.json();
                            const translatedText = data.translatedText;
                            this.state.translationCache.set(cacheKey, translatedText);
                            this.log(`LibreTranslate API ${i} successful`);
                            return translatedText;
                        } else {
                            this.log(`LibreTranslate API ${i} returned ${response.status}`, 'error');
                        }
                        
                    } catch (error) {
                        this.log(`LibreTranslate API ${i} failed: ${error.message}`, 'error');
                    }
                }
                
                throw new Error('All translation APIs failed or are blocked by CORS');
            },
            
            // UI Helper Methods
            setTranslatingState(isTranslating) {
                this.state.isTranslating = isTranslating;
                const buttons = document.querySelectorAll('.lang-btn');
                buttons.forEach(btn => btn.disabled = isTranslating);
                
                this.showStatus(isTranslating ? 'Translating...' : 'Ready');
            },
            
            updateLanguageState(languageCode, languageName) {
                document.querySelectorAll('.lang-btn').forEach(btn => {
                    btn.classList.remove('active');
                    if (btn.getAttribute('data-lang') === languageCode) {
                        btn.classList.add('active');
                    }
                });
                
                document.getElementById('current-language').textContent = languageName;
                this.state.currentLanguage = languageCode;
                document.documentElement.lang = languageCode;
            },
            
            showProgress(show) {
                const container = document.getElementById('progress-container');
                container.style.display = show ? 'block' : 'none';
            },
            
            updateProgress(percentage, message) {
                const fill = document.getElementById('progress-fill');
                const text = document.getElementById('progress-text');
                
                fill.style.width = `${percentage}%`;
                text.textContent = message;
            },
            
            showStatus(message) {
                document.getElementById('translation-status').textContent = message;
            },
            
            showError(message) {
                const errorEl = document.getElementById('error-message');
                errorEl.textContent = message;
                errorEl.style.display = 'block';
                setTimeout(() => this.hideError(), 8000);
            },
            
            hideError() {
                document.getElementById('error-message').style.display = 'none';
            },
            
            showSuccess(message) {
                const successEl = document.getElementById('success-message');
                successEl.textContent = message;
                successEl.style.display = 'block';
                setTimeout(() => successEl.style.display = 'none', 3000);
            },
            
            delay(ms) {
                return new Promise(resolve => setTimeout(resolve, ms));
            }
        };
        
        // Global function to handle language selection
        function translateToLanguage(languageCode, languageName) {
            TranslationSystem.translatePage(languageCode, languageName);
        }
        
        // Initialize the translation system when page loads
        document.addEventListener('DOMContentLoaded', function() {
            TranslationSystem.init();
        });