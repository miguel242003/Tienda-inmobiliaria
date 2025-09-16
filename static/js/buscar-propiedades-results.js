/**
 * BUSCAR PROPIEDADES RESULTS - RESULTS MANAGEMENT
 * ==============================================
 * Handles the search results display and interaction for the buscar propiedades page
 */

class BuscarPropiedadesResults {
    constructor() {
        this.resultsContainer = null;
        this.viewToggle = null;
        this.currentView = 'grid';
        this.isInitialized = false;
        this.animationDuration = 300;
        
        this.init();
    }

    /**
     * Initialize results section
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.bindEvents();
            this.setupAnimations();
            this.isInitialized = true;
            
            console.log('Buscar Propiedades Results initialized successfully');
        } catch (error) {
            console.error('Error initializing results:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.resultsContainer = document.getElementById('search-results');
        this.viewToggle = document.querySelector('.view-toggle');
    }

    /**
     * Bind events
     */
    bindEvents() {
        // View toggle buttons
        if (this.viewToggle) {
            this.viewToggle.addEventListener('click', (e) => this.handleViewToggle(e));
        }

        // Property card interactions
        this.setupPropertyCardInteractions();

        // Pagination
        this.setupPagination();

        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    /**
     * Handle view toggle
     */
    handleViewToggle(event) {
        const button = event.target.closest('.view-toggle-btn');
        if (!button) return;

        const view = button.dataset.view || (button.textContent.includes('th') ? 'grid' : 'list');
        this.changeView(view);
    }

    /**
     * Change view between grid and list
     */
    changeView(view) {
        if (view === this.currentView) return;

        // Update button states
        this.updateViewToggleButtons(view);

        // Animate view change
        this.animateViewChange(view);

        this.currentView = view;
    }

    /**
     * Update view toggle buttons
     */
    updateViewToggleButtons(view) {
        if (!this.viewToggle) return;

        const buttons = this.viewToggle.querySelectorAll('.view-toggle-btn');
        buttons.forEach(btn => {
            btn.classList.remove('active');
            const btnView = btn.dataset.view || (btn.textContent.includes('th') ? 'grid' : 'list');
            if (btnView === view) {
                btn.classList.add('active');
            }
        });
    }

    /**
     * Animate view change
     */
    animateViewChange(view) {
        if (!this.resultsContainer) return;

        // Add transition class
        this.resultsContainer.style.transition = `all ${this.animationDuration}ms ease`;
        
        // Change view class
        if (view === 'list') {
            this.resultsContainer.classList.add('list-view');
        } else {
            this.resultsContainer.classList.remove('list-view');
        }

        // Remove transition after animation
        setTimeout(() => {
            this.resultsContainer.style.transition = '';
        }, this.animationDuration);
    }

    /**
     * Setup property card interactions
     */
    setupPropertyCardInteractions() {
        if (!this.resultsContainer) return;

        const propertyCards = this.resultsContainer.querySelectorAll('.property-card');
        
        propertyCards.forEach(card => {
            // Hover effects
            card.addEventListener('mouseenter', () => this.handleCardHover(card));
            card.addEventListener('mouseleave', () => this.handleCardLeave(card));

            // Click tracking
            const link = card.querySelector('a[href*="detalle"]');
            if (link) {
                link.addEventListener('click', (e) => this.handlePropertyClick(e, card));
            }
        });
    }

    /**
     * Handle card hover
     */
    handleCardHover(card) {
        card.style.transform = 'translateY(-5px)';
        card.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.15)';
    }

    /**
     * Handle card leave
     */
    handleCardLeave(card) {
        card.style.transform = '';
        card.style.boxShadow = '';
    }

    /**
     * Handle property click
     */
    handlePropertyClick(event, card) {
        // Add click animation
        card.style.transform = 'scale(0.98)';
        
        setTimeout(() => {
            card.style.transform = '';
        }, 150);

        // Track click if tracking is available
        if (window.trackClick) {
            const propertyId = this.extractPropertyId(card);
            if (propertyId) {
                window.trackClick(propertyId, 'property_detail');
            }
        }
    }

    /**
     * Extract property ID from card
     */
    extractPropertyId(card) {
        const link = card.querySelector('a[href*="detalle"]');
        if (link) {
            const href = link.getAttribute('href');
            const match = href.match(/detalle\/(\d+)/);
            return match ? match[1] : null;
        }
        return null;
    }

    /**
     * Setup pagination
     */
    setupPagination() {
        const paginationLinks = document.querySelectorAll('.search-pagination-link');
        
        paginationLinks.forEach(link => {
            link.addEventListener('click', (e) => this.handlePaginationClick(e));
        });
    }

    /**
     * Handle pagination click
     */
    handlePaginationClick(event) {
        // Add loading state
        this.setLoadingState(true);
        
        // Scroll to top of results
        if (this.resultsContainer) {
            this.resultsContainer.scrollIntoView({ 
                behavior: 'smooth', 
                block: 'start' 
            });
        }
    }

    /**
     * Setup animations
     */
    setupAnimations() {
        if (!this.resultsContainer) return;

        // Animate cards on load
        const cards = this.resultsContainer.querySelectorAll('.property-card');
        
        cards.forEach((card, index) => {
            card.style.opacity = '0';
            card.style.transform = 'translateY(30px)';
            
            setTimeout(() => {
                card.style.transition = 'all 0.6s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 100);
        });
    }

    /**
     * Handle keyboard navigation
     */
    handleKeyboard(event) {
        // Escape key to clear filters
        if (event.key === 'Escape') {
            this.clearFilters();
        }
        
        // Arrow keys for view toggle
        if (event.key === 'ArrowLeft' || event.key === 'ArrowRight') {
            event.preventDefault();
            this.toggleView();
        }
    }

    /**
     * Toggle between grid and list view
     */
    toggleView() {
        const newView = this.currentView === 'grid' ? 'list' : 'grid';
        this.changeView(newView);
    }

    /**
     * Clear filters
     */
    clearFilters() {
        if (window.buscarPropiedadesFilters) {
            window.buscarPropiedadesFilters.resetForm();
        }
    }

    /**
     * Set loading state
     */
    setLoadingState(loading) {
        if (loading) {
            this.resultsContainer.classList.add('loading');
        } else {
            this.resultsContainer.classList.remove('loading');
        }
    }

    /**
     * Refresh results
     */
    refreshResults() {
        this.setLoadingState(true);
        
        // Reload page or fetch new results
        window.location.reload();
    }

    /**
     * Get current view
     */
    getCurrentView() {
        return this.currentView;
    }

    /**
     * Get results count
     */
    getResultsCount() {
        if (!this.resultsContainer) return 0;
        
        const cards = this.resultsContainer.querySelectorAll('.property-card');
        return cards.length;
    }

    /**
     * Get results state
     */
    getResultsState() {
        return {
            isInitialized: this.isInitialized,
            currentView: this.currentView,
            resultsCount: this.getResultsCount()
        };
    }

    /**
     * Destroy results
     */
    destroy() {
        if (this.viewToggle) {
            this.viewToggle.removeEventListener('click', this.handleViewToggle);
        }
        
        document.removeEventListener('keydown', this.handleKeyboard);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.BuscarPropiedadesResults = BuscarPropiedadesResults;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.buscarPropiedadesResults = new BuscarPropiedadesResults();
});
