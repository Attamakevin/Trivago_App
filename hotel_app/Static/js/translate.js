// Simple Google Translate with limited languages
function googleTranslateElementInit() {
    new google.translate.TranslateElement({
        pageLanguage: 'en',
        includedLanguages: 'en,es,zh,de,it,pt,nl,ru,ja,ko',
        layout: google.translate.TranslateElement.InlineLayout.SIMPLE,
        autoDisplay: false
    }, 'google_translate_element');
}

document.addEventListener('DOMContentLoaded', function () {
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
    }, 2000);
});