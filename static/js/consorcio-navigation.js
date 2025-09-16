/**
 * CONSORCIO NAVIGATION - NAVIGATION MANAGEMENT
 * ==========================================
 * Handles the navigation functionality for the consorcio page
 */

class ConsorcioNavigation {
    constructor() {
        this.navItems = [];
        this.mobileMenuBtn = null;
        this.mobileMenuPanel = null;
        this.mobileOverlay = null;
        this.isMobileMenuOpen = false;
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Initialize navigation
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.bindEvents();
            this.setupScrollBehavior();
            this.isInitialized = true;
            
            console.log('Consorcio Navigation initialized successfully');
        } catch (error) {
            console.error('Error initializing navigation:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.navItems = document.querySelectorAll('.nav-item');
        this.mobileMenuBtn = document.getElementById('mobileMenuBtn');
        this.mobileMenuPanel = document.getElementById('mobileMenuPanel');
        this.mobileOverlay = document.getElementById('mobileOverlay');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Desktop navigation
        this.navItems.forEach(item => {
            item.addEventListener('click', (e) => this.handleNavClick(e, item));
            item.addEventListener('mouseenter', () => this.handleNavHover(item));
            item.addEventListener('mouseleave', () => this.handleNavLeave(item));
        });

        // Mobile menu
        if (this.mobileMenuBtn) {
            this.mobileMenuBtn.addEventListener('click', () => this.toggleMobileMenu());
        }

        if (this.mobileOverlay) {
            this.mobileOverlay.addEventListener('click', () => this.closeMobileMenu());
        }

        // Close mobile menu on escape
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));

        // Close mobile menu on window resize
        window.addEventListener('resize', () => this.handleResize());
    }

    /**
     * Handle navigation click
     */
    handleNavClick(event, item) {
        // If it's the active link (CONSORCIO), scroll to content
        if (item.classList.contains('active')) {
            event.preventDefault();
            this.scrollToContent();
            return false;
        }
        
        // Visual feedback for non-active links
        this.showClickFeedback(item);
    }

    /**
     * Handle navigation hover
     */
    handleNavHover(item) {
        if (!item.classList.contains('active')) {
            item.style.transition = 'all 0.05s ease-out';
            item.style.transform = 'translateY(-1px)';
            item.style.backgroundColor = 'rgba(43, 85, 162, 0.15)';
        }
    }

    /**
     * Handle navigation leave
     */
    handleNavLeave(item) {
        if (!item.classList.contains('active')) {
            item.style.transform = '';
            item.style.backgroundColor = '';
        }
    }

    /**
     * Show click feedback
     */
    showClickFeedback(item) {
        item.style.transition = 'all 0.05s ease-out';
        item.style.transform = 'translateY(-1px)';
        item.style.backgroundColor = 'rgba(43, 85, 162, 0.15)';
        
        // Restore immediately
        setTimeout(() => {
            item.style.transform = '';
            item.style.backgroundColor = '';
        }, 50);
    }

    /**
     * Scroll to content
     */
    scrollToContent() {
        const consorcioContent = document.querySelector('.consorcio-content');
        if (consorcioContent) {
            const navHeight = 60;
            const extraOffset = -60;
            const targetPosition = consorcioContent.offsetTop - navHeight - extraOffset;
            
            // Smooth scroll
            window.scrollTo({
                top: targetPosition,
                behavior: 'smooth'
            });
        }
    }

    /**
     * Toggle mobile menu
     */
    toggleMobileMenu() {
        this.isMobileMenuOpen = !this.isMobileMenuOpen;
        
        if (this.isMobileMenuOpen) {
            this.openMobileMenu();
        } else {
            this.closeMobileMenu();
        }
    }

    /**
     * Open mobile menu
     */
    openMobileMenu() {
        if (this.mobileMenuPanel) {
            this.mobileMenuPanel.classList.add('active');
        }
        
        if (this.mobileOverlay) {
            this.mobileOverlay.classList.add('active');
        }
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
        
        this.isMobileMenuOpen = true;
    }

    /**
     * Close mobile menu
     */
    closeMobileMenu() {
        if (this.mobileMenuPanel) {
            this.mobileMenuPanel.classList.remove('active');
        }
        
        if (this.mobileOverlay) {
            this.mobileOverlay.classList.remove('active');
        }
        
        // Restore body scroll
        document.body.style.overflow = '';
        
        this.isMobileMenuOpen = false;
    }

    /**
     * Handle keyboard events
     */
    handleKeyboard(event) {
        // Close mobile menu on escape
        if (event.key === 'Escape' && this.isMobileMenuOpen) {
            this.closeMobileMenu();
        }
    }

    /**
     * Handle window resize
     */
    handleResize() {
        // Close mobile menu on desktop
        if (window.innerWidth > 992 && this.isMobileMenuOpen) {
            this.closeMobileMenu();
        }
    }

    /**
     * Setup scroll behavior
     */
    setupScrollBehavior() {
        // Auto-scroll to content on page load
        if (window.location.pathname.includes('consorcio')) {
            // Small delay to ensure content is loaded
            setTimeout(() => {
                this.scrollToContent();
            }, 100);
        }
    }

    /**
     * Get mobile menu state
     */
    isMobileMenuOpen() {
        return this.isMobileMenuOpen;
    }

    /**
     * Destroy navigation
     */
    destroy() {
        // Remove event listeners
        this.navItems.forEach(item => {
            item.removeEventListener('click', this.handleNavClick);
            item.removeEventListener('mouseenter', this.handleNavHover);
            item.removeEventListener('mouseleave', this.handleNavLeave);
        });
        
        if (this.mobileMenuBtn) {
            this.mobileMenuBtn.removeEventListener('click', this.toggleMobileMenu);
        }
        
        if (this.mobileOverlay) {
            this.mobileOverlay.removeEventListener('click', this.closeMobileMenu);
        }
        
        document.removeEventListener('keydown', this.handleKeyboard);
        window.removeEventListener('resize', this.handleResize);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.ConsorcioNavigation = ConsorcioNavigation;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.consorcioNavigation = new ConsorcioNavigation();
});
