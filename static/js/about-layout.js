/**
 * ABOUT LAYOUT - LAYOUT MANAGEMENT
 * ================================
 * Handles the about page layout and responsive behavior
 */

class AboutLayout {
    constructor() {
        this.aboutSection = null;
        this.valuesSection = null;
        this.isInitialized = false;
        this.currentBreakpoint = null;
        this.originalCardPositions = [];
        
        this.init();
    }

    /**
     * Initialize layout
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupResponsive();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('About Layout initialized successfully');
        } catch (error) {
            console.error('Error initializing about layout:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.aboutSection = document.querySelector('.about-main-section');
        this.valuesSection = document.querySelector('.about-values-hero');
    }

    /**
     * Setup responsive behavior
     */
    setupResponsive() {
        this.updateLayout();
        this.setupBreakpointDetection();
        this.storeOriginalCardPositions();
    }

    /**
     * Store original card positions
     */
    storeOriginalCardPositions() {
        const cards = document.querySelectorAll('.about-value-card');
        this.originalCardPositions = Array.from(cards).map((card, index) => {
            const positions = [160, 110, 160, 110];
            return positions[index] || 0;
        });
    }

    /**
     * Setup breakpoint detection
     */
    setupBreakpointDetection() {
        const breakpoints = {
            mobile: 575,
            tablet: 767,
            tabletLarge: 991,
            desktop: 1200
        };
        
        const checkBreakpoint = () => {
            const width = window.innerWidth;
            let newBreakpoint = 'desktop';
            
            if (width <= breakpoints.mobile) {
                newBreakpoint = 'mobile';
            } else if (width <= breakpoints.tablet) {
                newBreakpoint = 'tablet';
            } else if (width <= breakpoints.tabletLarge) {
                newBreakpoint = 'tabletLarge';
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
            case 'tabletLarge':
                this.handleTabletLargeLayout();
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
        if (!this.aboutSection) return;
        
        // Update about section
        this.aboutSection.style.gridTemplateColumns = '1fr';
        this.aboutSection.style.height = 'auto';
        this.aboutSection.style.minHeight = '300px';
        this.aboutSection.style.padding = '20px 0';
        
        // Update values section
        this.updateValuesLayout('mobile');
    }

    /**
     * Handle tablet layout
     */
    handleTabletLayout() {
        if (!this.aboutSection) return;
        
        // Update about section
        this.aboutSection.style.gridTemplateColumns = '1fr';
        this.aboutSection.style.height = 'auto';
        this.aboutSection.style.minHeight = '350px';
        this.aboutSection.style.padding = '30px 0';
        
        // Update values section
        this.updateValuesLayout('tablet');
    }

    /**
     * Handle tablet large layout
     */
    handleTabletLargeLayout() {
        if (!this.aboutSection) return;
        
        // Update about section
        this.aboutSection.style.gridTemplateColumns = '1fr';
        this.aboutSection.style.height = 'auto';
        this.aboutSection.style.minHeight = '400px';
        this.aboutSection.style.padding = '40px 0';
        
        // Update values section
        this.updateValuesLayout('tabletLarge');
    }

    /**
     * Handle desktop layout
     */
    handleDesktopLayout() {
        if (!this.aboutSection) return;
        
        // Update about section
        this.aboutSection.style.gridTemplateColumns = '50% 50%';
        this.aboutSection.style.height = '600px';
        this.aboutSection.style.minHeight = '600px';
        this.aboutSection.style.padding = '60px 0';
        
        // Update values section
        this.updateValuesLayout('desktop');
    }

    /**
     * Update values layout
     */
    updateValuesLayout(breakpoint) {
        const cards = document.querySelectorAll('.about-value-card');
        
        cards.forEach((card, index) => {
            switch (breakpoint) {
                case 'mobile':
                    card.style.transform = 'translateY(0)';
                    break;
                case 'tablet':
                    const tabletPositions = [100, 60, 100, 60];
                    card.style.transform = `translateY(${tabletPositions[index]}px)`;
                    break;
                case 'tabletLarge':
                    const tabletLargePositions = [120, 80, 120, 80];
                    card.style.transform = `translateY(${tabletLargePositions[index]}px)`;
                    break;
                case 'desktop':
                    const desktopPositions = [160, 110, 160, 110];
                    card.style.transform = `translateY(${desktopPositions[index]}px)`;
                    break;
            }
        });
    }

    /**
     * Update layout
     */
    updateLayout() {
        const width = window.innerWidth;
        
        if (width <= 575) {
            this.handleMobileLayout();
        } else if (width <= 767) {
            this.handleTabletLayout();
        } else if (width <= 991) {
            this.handleTabletLargeLayout();
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
        
        // Scroll events for layout adjustments
        window.addEventListener('scroll', () => this.handleScroll());
    }

    /**
     * Handle scroll events
     */
    handleScroll() {
        const scrolled = window.pageYOffset;
        const windowHeight = window.innerHeight;
        
        // Adjust card positions based on scroll
        if (this.currentBreakpoint === 'desktop') {
            const cards = document.querySelectorAll('.about-value-card');
            cards.forEach((card, index) => {
                const cardTop = card.offsetTop;
                const cardHeight = card.offsetHeight;
                const progress = Math.min(
                    Math.max((scrolled - cardTop + windowHeight) / cardHeight, 0),
                    1
                );
                
                const originalY = this.originalCardPositions[index] || 0;
                const adjustedY = originalY - (progress * 20);
                card.style.transform = `translateY(${adjustedY}px)`;
            });
        }
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
            hasAboutSection: !!this.aboutSection,
            hasValuesSection: !!this.valuesSection
        };
    }

    /**
     * Destroy layout
     */
    destroy() {
        window.removeEventListener('resize', this.updateLayout);
        window.removeEventListener('orientationchange', this.updateLayout);
        window.removeEventListener('scroll', this.handleScroll);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.AboutLayout = AboutLayout;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aboutLayout = new AboutLayout();
});
