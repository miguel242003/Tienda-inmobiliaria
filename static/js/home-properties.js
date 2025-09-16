/**
 * HOME PROPERTIES - PROPERTIES SECTION MANAGEMENT
 * ==============================================
 * Handles the properties section functionality
 */

class HomeProperties {
    constructor() {
        this.alquilerBtn = null;
        this.alquilerTemporalBtn = null;
        this.alquilerContainer = null;
        this.alquilerTemporalContainer = null;
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Initialize properties section
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.bindEvents();
            this.setDefaultView();
            this.isInitialized = true;
            
            console.log('Home Properties initialized successfully');
        } catch (error) {
            console.error('Error initializing properties:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.alquilerBtn = document.getElementById('btn-alquiler');
        this.alquilerTemporalBtn = document.getElementById('btn-alquiler-temporal');
        this.alquilerContainer = document.getElementById('propiedades-alquiler');
        this.alquilerTemporalContainer = document.getElementById('propiedades-alquiler-temporal');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        if (this.alquilerBtn) {
            this.alquilerBtn.addEventListener('change', () => this.handleAlquilerChange());
        }
        
        if (this.alquilerTemporalBtn) {
            this.alquilerTemporalBtn.addEventListener('change', () => this.handleAlquilerTemporalChange());
        }
    }

    /**
     * Handle alquiler button change
     */
    handleAlquilerChange() {
        if (this.alquilerBtn.checked) {
            this.showAlquiler();
        }
    }

    /**
     * Handle alquiler temporal button change
     */
    handleAlquilerTemporalChange() {
        if (this.alquilerTemporalBtn.checked) {
            this.showAlquilerTemporal();
        }
    }

    /**
     * Show alquiler properties
     */
    showAlquiler() {
        if (!this.alquilerContainer || !this.alquilerTemporalContainer) return;
        
        // Show alquiler container
        this.alquilerContainer.style.display = 'flex';
        this.alquilerTemporalContainer.style.display = 'none';
        
        // Update button styles
        this.updateButtonStyles('alquiler');
        
        // Trigger custom event
        this.dispatchEvent('propertiesViewChanged', { view: 'alquiler' });
    }

    /**
     * Show alquiler temporal properties
     */
    showAlquilerTemporal() {
        if (!this.alquilerContainer || !this.alquilerTemporalContainer) return;
        
        // Show alquiler temporal container
        this.alquilerContainer.style.display = 'none';
        this.alquilerTemporalContainer.style.display = 'flex';
        
        // Update button styles
        this.updateButtonStyles('alquiler_temporal');
        
        // Trigger custom event
        this.dispatchEvent('propertiesViewChanged', { view: 'alquiler_temporal' });
    }

    /**
     * Update button styles
     */
    updateButtonStyles(activeView) {
        if (activeView === 'alquiler') {
            this.alquilerBtn.classList.remove('btn-outline-primary');
            this.alquilerBtn.classList.add('btn-primary');
            this.alquilerTemporalBtn.classList.remove('btn-primary');
            this.alquilerTemporalBtn.classList.add('btn-outline-primary');
        } else {
            this.alquilerTemporalBtn.classList.remove('btn-outline-primary');
            this.alquilerTemporalBtn.classList.add('btn-primary');
            this.alquilerBtn.classList.remove('btn-primary');
            this.alquilerBtn.classList.add('btn-outline-primary');
        }
    }

    /**
     * Set default view
     */
    setDefaultView() {
        // Show alquiler temporal by default
        this.showAlquilerTemporal();
    }

    /**
     * Get current view
     */
    getCurrentView() {
        if (this.alquilerBtn && this.alquilerBtn.checked) {
            return 'alquiler';
        } else if (this.alquilerTemporalBtn && this.alquilerTemporalBtn.checked) {
            return 'alquiler_temporal';
        }
        return null;
    }

    /**
     * Switch to specific view
     */
    switchToView(view) {
        if (view === 'alquiler') {
            this.showAlquiler();
        } else if (view === 'alquiler_temporal') {
            this.showAlquilerTemporal();
        }
    }

    /**
     * Check if alquiler has properties
     */
    hasAlquilerProperties() {
        if (!this.alquilerContainer) return false;
        const properties = this.alquilerContainer.querySelectorAll('.col-md-6');
        return properties.length > 0;
    }

    /**
     * Check if alquiler temporal has properties
     */
    hasAlquilerTemporalProperties() {
        if (!this.alquilerTemporalContainer) return false;
        const properties = this.alquilerTemporalContainer.querySelectorAll('.col-md-6');
        return properties.length > 0;
    }

    /**
     * Get property count for current view
     */
    getCurrentViewPropertyCount() {
        const currentView = this.getCurrentView();
        if (currentView === 'alquiler') {
            return this.getAlquilerPropertyCount();
        } else if (currentView === 'alquiler_temporal') {
            return this.getAlquilerTemporalPropertyCount();
        }
        return 0;
    }

    /**
     * Get alquiler property count
     */
    getAlquilerPropertyCount() {
        if (!this.alquilerContainer) return 0;
        return this.alquilerContainer.querySelectorAll('.col-md-6').length;
    }

    /**
     * Get alquiler temporal property count
     */
    getAlquilerTemporalPropertyCount() {
        if (!this.alquilerTemporalContainer) return 0;
        return this.alquilerTemporalContainer.querySelectorAll('.col-md-6').length;
    }

    /**
     * Dispatch custom event
     */
    dispatchEvent(eventName, detail) {
        const event = new CustomEvent(eventName, { detail });
        document.dispatchEvent(event);
    }

    /**
     * Refresh properties section
     */
    refresh() {
        this.cacheElements();
        this.setDefaultView();
    }

    /**
     * Destroy properties section
     */
    destroy() {
        if (this.alquilerBtn) {
            this.alquilerBtn.removeEventListener('change', this.handleAlquilerChange);
        }
        
        if (this.alquilerTemporalBtn) {
            this.alquilerTemporalBtn.removeEventListener('change', this.handleAlquilerTemporalChange);
        }
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.HomeProperties = HomeProperties;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.homeProperties = new HomeProperties();
});
