/**
 * CV LAYOUT - LAYOUT MANAGEMENT
 * ============================
 * Handles the CV layout and responsive behavior
 */

class CVLayout {
    constructor() {
        this.applicationSection = null;
        this.imageSection = null;
        this.formSection = null;
        this.isInitialized = false;
        this.currentBreakpoint = null;
        
        this.init();
    }

    /**
     * Initialize CV layout
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupResponsive();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('CV Layout initialized successfully');
        } catch (error) {
            console.error('Error initializing CV layout:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.applicationSection = document.querySelector('.cv-application-section');
        
        if (this.applicationSection) {
            this.imageSection = this.applicationSection.querySelector('.cv-image-section');
            this.formSection = this.applicationSection.querySelector('.cv-form-section');
        }
    }

    /**
     * Setup responsive behavior
     */
    setupResponsive() {
        this.updateLayout();
        this.setupBreakpointDetection();
    }

    /**
     * Setup breakpoint detection
     */
    setupBreakpointDetection() {
        const breakpoints = {
            mobile: 767,
            tablet: 1199,
            desktop: 1200
        };
        
        const checkBreakpoint = () => {
            const width = window.innerWidth;
            let newBreakpoint = 'desktop';
            
            if (width <= breakpoints.mobile) {
                newBreakpoint = 'mobile';
            } else if (width <= breakpoints.tablet) {
                newBreakpoint = 'tablet';
            }
            
            if (newBreakpoint !== this.currentBreakpoint) {
                this.currentBreakpoint = newBreakpoint;
                this.handleBreakpointChange(newBreakpoint);
            }
        };
        
        // Initial check
        checkBreakpoint();
        
        // Listen for resize events
        window.addEventListener('resize', this.debounce(checkBreakpoint, 250));
    }

    /**
     * Handle breakpoint change
     */
    handleBreakpointChange(breakpoint) {
        console.log('Breakpoint changed to:', breakpoint);
        
        switch (breakpoint) {
            case 'mobile':
                this.handleMobileLayout();
                break;
            case 'tablet':
                this.handleTabletLayout();
                break;
            case 'desktop':
                this.handleDesktopLayout();
                break;
        }
    }

    /**
     * Handle mobile layout
     */
    handleMobileLayout() {
        if (!this.applicationSection) return;
        
        // Update section styles
        this.applicationSection.style.width = '100%';
        this.applicationSection.style.maxWidth = '100%';
        this.applicationSection.style.margin = '40px auto';
        this.applicationSection.style.padding = '0 16px';
        this.applicationSection.style.height = 'auto';
        this.applicationSection.style.minHeight = 'auto';
        
        // Update image section
        if (this.imageSection) {
            this.imageSection.style.order = '-1';
            this.imageSection.style.height = '300px';
            this.imageSection.style.marginBottom = '20px';
        }
        
        // Update form section
        if (this.formSection) {
            this.formSection.style.padding = '20px';
        }
    }

    /**
     * Handle tablet layout
     */
    handleTabletLayout() {
        if (!this.applicationSection) return;
        
        // Update section styles
        this.applicationSection.style.width = '100%';
        this.applicationSection.style.maxWidth = '1320px';
        this.applicationSection.style.margin = '60px auto';
        this.applicationSection.style.padding = '0 32px';
        this.applicationSection.style.height = 'auto';
        this.applicationSection.style.minHeight = '600px';
        
        // Hide image section
        if (this.imageSection) {
            this.imageSection.style.display = 'none';
        }
        
        // Update form section
        if (this.formSection) {
            this.formSection.style.flex = '0 0 100%';
            this.formSection.style.maxWidth = '100%';
            this.formSection.style.width = '100%';
        }
    }

    /**
     * Handle desktop layout
     */
    handleDesktopLayout() {
        if (!this.applicationSection) return;
        
        // Update section styles
        this.applicationSection.style.width = '1400px';
        this.applicationSection.style.height = '750px';
        this.applicationSection.style.margin = '60px auto';
        this.applicationSection.style.padding = '0';
        
        // Show image section
        if (this.imageSection) {
            this.imageSection.style.display = 'block';
            this.imageSection.style.order = '';
            this.imageSection.style.height = '';
            this.imageSection.style.marginBottom = '';
        }
        
        // Update form section
        if (this.formSection) {
            this.formSection.style.flex = '0 0 66.666667%';
            this.formSection.style.maxWidth = '';
            this.formSection.style.width = '';
            this.formSection.style.padding = '40px';
        }
    }

    /**
     * Update layout
     */
    updateLayout() {
        const width = window.innerWidth;
        
        if (width <= 767) {
            this.handleMobileLayout();
        } else if (width <= 1199) {
            this.handleTabletLayout();
        } else {
            this.handleDesktopLayout();
        }
    }

    /**
     * Bind events
     */
    bindEvents() {
        // Window resize
        window.addEventListener('resize', () => this.updateLayout());
        
        // Orientation change
        window.addEventListener('orientationchange', () => {
            setTimeout(() => this.updateLayout(), 100);
        });
    }

    /**
     * Debounce function
     */
    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    /**
     * Get current breakpoint
     */
    getCurrentBreakpoint() {
        return this.currentBreakpoint;
    }

    /**
     * Get layout state
     */
    getLayoutState() {
        return {
            isInitialized: this.isInitialized,
            currentBreakpoint: this.currentBreakpoint,
            hasImageSection: !!this.imageSection,
            hasFormSection: !!this.formSection
        };
    }

    /**
     * Destroy layout
     */
    destroy() {
        window.removeEventListener('resize', this.updateLayout);
        window.removeEventListener('orientationchange', this.updateLayout);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.CVLayout = CVLayout;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.cvLayout = new CVLayout();
});
