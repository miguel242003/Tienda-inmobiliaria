/**
 * Nominatim Autocomplete para el campo de ubicación
 * Integración con Nominatim (OpenStreetMap) para autocompletado de direcciones
 * 100% gratuito, sin API key, sin registro
 */

class NominatimAutocomplete {
    constructor() {
        this.inputElement = null;
        this.isInitialized = false;
        this.config = null;
        this.suggestionsContainer = null;
        this.currentSuggestions = [];
        this.lastRequestTime = 0;
        this.requestDelay = 1000; // 1 segundo entre requests
        this.cache = new Map();
        this.cacheTimeout = 5 * 60 * 1000; // 5 minutos
    }

    /**
     * Inicializar el autocompletado de Nominatim
     * @param {string} inputId - ID del input donde se aplicará el autocompletado
     * @param {object} config - Configuración del autocompletado
     */
    async init(inputId, config = {}) {
        try {
            this.config = {
                baseUrl: 'https://nominatim.openstreetmap.org/search',
                countryCodes: 'ar',
                format: 'json',
                addressdetails: 1,
                limit: 5,
                dedupe: 1,
                extratags: 1,
                namedetails: 1,
                ...config
            };
            
            this.inputElement = document.getElementById(inputId);
            
            if (!this.inputElement) {
                console.error(`No se encontró el elemento con ID: ${inputId}`);
                return false;
            }

            this.setupAutocomplete();
            this.isInitialized = true;
            
            console.log('Nominatim Autocomplete inicializado correctamente');
            return true;
            
        } catch (error) {
            console.error('Error al inicializar Nominatim Autocomplete:', error);
            return false;
        }
    }

    /**
     * Configurar el autocompletado
     */
    setupAutocomplete() {
        // Crear contenedor para las sugerencias
        this.createSuggestionsContainer();
        
        // Agregar event listeners
        this.inputElement.addEventListener('input', (e) => {
            this.handleInput(e.target.value);
        });
        
        this.inputElement.addEventListener('keydown', (e) => {
            this.handleKeydown(e);
        });
        
        this.inputElement.addEventListener('blur', () => {
            // Delay para permitir hacer clic en las sugerencias
            setTimeout(() => {
                this.hideSuggestions();
            }, 200);
        });
        
        this.inputElement.addEventListener('focus', () => {
            if (this.currentSuggestions.length > 0) {
                this.showSuggestions();
            }
        });

        // Agregar estilos CSS
        this.addAutocompleteStyles();
    }

    /**
     * Crear contenedor para las sugerencias
     */
    createSuggestionsContainer() {
        this.suggestionsContainer = document.createElement('div');
        this.suggestionsContainer.className = 'nominatim-suggestions';
        this.suggestionsContainer.style.display = 'none';
        
        // Insertar después del input
        this.inputElement.parentNode.insertBefore(
            this.suggestionsContainer, 
            this.inputElement.nextSibling
        );
    }

    /**
     * Manejar el input del usuario
     */
    async handleInput(query) {
        if (query.length < 3) {
            this.hideSuggestions();
            return;
        }

        // Rate limiting: esperar 1 segundo entre requests
        const now = Date.now();
        if (now - this.lastRequestTime < this.requestDelay) {
            return;
        }

        // Verificar cache
        const cacheKey = query.toLowerCase().trim();
        if (this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < this.cacheTimeout) {
                this.displaySuggestions(cached.data);
                return;
            } else {
                this.cache.delete(cacheKey);
            }
        }

        this.lastRequestTime = now;
        
        try {
            const suggestions = await this.fetchSuggestions(query);
            this.cache.set(cacheKey, {
                data: suggestions,
                timestamp: Date.now()
            });
            this.displaySuggestions(suggestions);
        } catch (error) {
            console.error('Error al obtener sugerencias:', error);
            this.hideSuggestions();
        }
    }

    /**
     * Obtener sugerencias de Nominatim
     */
    async fetchSuggestions(query) {
        const params = new URLSearchParams({
            q: query,
            countrycodes: this.config.countryCodes,
            format: this.config.format,
            addressdetails: this.config.addressdetails,
            limit: this.config.limit,
            dedupe: this.config.dedupe,
            extratags: this.config.extratags,
            namedetails: this.config.namedetails
        });

        const url = `${this.config.baseUrl}?${params}`;
        
        const response = await fetch(url, {
            headers: {
                'User-Agent': 'TiendaInmobiliaria/1.0 (contact@tiendainmobiliaria.com)'
            }
        });

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const data = await response.json();
        return data.map(item => this.formatSuggestion(item));
    }

    /**
     * Formatear sugerencia de Nominatim
     */
    formatSuggestion(item) {
        const address = item.address || {};
        const displayName = item.display_name;
        
        // Crear dirección más legible
        let shortAddress = '';
        if (address.road) shortAddress += address.road;
        if (address.house_number) shortAddress += ` ${address.house_number}`;
        if (address.suburb && !shortAddress) shortAddress = address.suburb;
        if (address.city && !shortAddress) shortAddress = address.city;
        if (address.state) shortAddress += `, ${address.state}`;
        if (address.country) shortAddress += `, ${address.country}`;
        
        return {
            displayName: displayName,
            shortAddress: shortAddress || displayName,
            lat: parseFloat(item.lat),
            lon: parseFloat(item.lon),
            placeId: item.place_id,
            type: item.type,
            importance: item.importance,
            original: item
        };
    }

    /**
     * Mostrar sugerencias
     */
    displaySuggestions(suggestions) {
        this.currentSuggestions = suggestions;
        
        if (suggestions.length === 0) {
            this.hideSuggestions();
            return;
        }

        this.suggestionsContainer.innerHTML = '';
        
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'nominatim-suggestion-item';
            item.dataset.index = index;
            
            item.innerHTML = `
                <div class="suggestion-content">
                    <div class="suggestion-address">${suggestion.shortAddress}</div>
                    <div class="suggestion-type">${suggestion.type}</div>
                </div>
            `;
            
            item.addEventListener('click', () => {
                this.selectSuggestion(suggestion);
            });
            
            item.addEventListener('mouseenter', () => {
                this.highlightSuggestion(index);
            });
            
            this.suggestionsContainer.appendChild(item);
        });
        
        this.showSuggestions();
    }

    /**
     * Mostrar el contenedor de sugerencias
     */
    showSuggestions() {
        this.suggestionsContainer.style.display = 'block';
    }

    /**
     * Ocultar el contenedor de sugerencias
     */
    hideSuggestions() {
        this.suggestionsContainer.style.display = 'none';
    }

    /**
     * Resaltar sugerencia
     */
    highlightSuggestion(index) {
        const items = this.suggestionsContainer.querySelectorAll('.nominatim-suggestion-item');
        items.forEach((item, i) => {
            item.classList.toggle('highlighted', i === index);
        });
    }

    /**
     * Seleccionar sugerencia
     */
    selectSuggestion(suggestion) {
        this.inputElement.value = suggestion.shortAddress;
        this.hideSuggestions();
        
        // Disparar evento personalizado
        const event = new CustomEvent('placeSelected', {
            detail: {
                suggestion: suggestion,
                formattedAddress: suggestion.shortAddress,
                displayName: suggestion.displayName,
                lat: suggestion.lat,
                lon: suggestion.lon,
                placeId: suggestion.placeId,
                type: suggestion.type
            }
        });
        
        this.inputElement.dispatchEvent(event);

        // Log para debugging
        console.log('Lugar seleccionado:', {
            address: suggestion.shortAddress,
            lat: suggestion.lat,
            lon: suggestion.lon,
            type: suggestion.type
        });
    }

    /**
     * Manejar teclado
     */
    handleKeydown(e) {
        const items = this.suggestionsContainer.querySelectorAll('.nominatim-suggestion-item');
        const highlighted = this.suggestionsContainer.querySelector('.highlighted');
        
        if (e.key === 'ArrowDown') {
            e.preventDefault();
            if (highlighted) {
                const next = highlighted.nextElementSibling;
                if (next) {
                    this.highlightSuggestion(parseInt(next.dataset.index));
                }
            } else if (items.length > 0) {
                this.highlightSuggestion(0);
            }
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            if (highlighted) {
                const prev = highlighted.previousElementSibling;
                if (prev) {
                    this.highlightSuggestion(parseInt(prev.dataset.index));
                }
            }
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (highlighted) {
                const index = parseInt(highlighted.dataset.index);
                this.selectSuggestion(this.currentSuggestions[index]);
            }
        } else if (e.key === 'Escape') {
            this.hideSuggestions();
        }
    }

    /**
     * Agregar estilos CSS para las sugerencias del autocompletado
     */
    addAutocompleteStyles() {
        const styleId = 'nominatim-autocomplete-styles';
        
        // Verificar si ya existen los estilos
        if (document.getElementById(styleId)) {
            return;
        }

        const style = document.createElement('style');
        style.id = styleId;
        style.textContent = `
            .nominatim-suggestions {
                background-color: #fff;
                border: 1px solid #d1d5db;
                border-radius: 8px;
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                margin-top: 4px;
                max-height: 300px;
                overflow-y: auto;
                z-index: 1000;
                position: absolute;
                width: 100%;
                min-width: 300px;
            }
            
            .nominatim-suggestion-item {
                border-bottom: 1px solid #f3f4f6;
                cursor: pointer;
                padding: 12px 16px;
                transition: background-color 0.2s ease;
                display: flex;
                align-items: center;
            }
            
            .nominatim-suggestion-item:last-child {
                border-bottom: none;
            }
            
            .nominatim-suggestion-item:hover,
            .nominatim-suggestion-item.highlighted {
                background-color: #f8fafc;
            }
            
            .suggestion-content {
                flex: 1;
            }
            
            .suggestion-address {
                color: #1f2937;
                font-size: 14px;
                font-weight: 500;
                margin-bottom: 2px;
            }
            
            .suggestion-type {
                color: #6b7280;
                font-size: 12px;
                text-transform: capitalize;
            }
            
            .nominatim-suggestion-item::before {
                content: '📍';
                margin-right: 8px;
                font-size: 16px;
            }
            
            /* Loading indicator */
            .nominatim-loading {
                padding: 12px 16px;
                text-align: center;
                color: #6b7280;
                font-size: 14px;
            }
            
            .nominatim-loading::after {
                content: '';
                display: inline-block;
                width: 16px;
                height: 16px;
                border: 2px solid #e5e7eb;
                border-top: 2px solid #3b82f6;
                border-radius: 50%;
                animation: spin 1s linear infinite;
                margin-left: 8px;
            }
            
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Limpiar el autocompletado
     */
    clear() {
        if (this.inputElement) {
            this.inputElement.value = '';
        }
        this.hideSuggestions();
        this.currentSuggestions = [];
    }

    /**
     * Destruir la instancia del autocompletado
     */
    destroy() {
        if (this.suggestionsContainer) {
            this.suggestionsContainer.remove();
        }
        
        this.inputElement = null;
        this.suggestionsContainer = null;
        this.isInitialized = false;
        this.cache.clear();
    }
}

// Instancia global para uso fácil
window.nominatimAutocomplete = new NominatimAutocomplete();

// Función de utilidad para inicializar fácilmente
window.initLocationAutocomplete = function(inputId, config = {}) {
    return window.nominatimAutocomplete.init(inputId, config);
};

// Auto-inicialización si hay un elemento con data-nominatim
document.addEventListener('DOMContentLoaded', function() {
    const locationInputs = document.querySelectorAll('[data-nominatim]');
    
    locationInputs.forEach(input => {
        const config = input.dataset.nominatimConfig ? 
            JSON.parse(input.dataset.nominatimConfig) : {};
        
        window.initLocationAutocomplete(input.id, config);
    });
});
