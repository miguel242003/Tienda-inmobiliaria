/**
 * CV BENEFITS - BENEFITS SECTION MANAGEMENT
 * =======================================
 * Handles the benefits section animations and interactions for the CV page
 */

class CVBenefits {
    constructor() {
        this.benefitsSection = null;
        this.benefitItems = [];
        this.isInitialized = false;
        this.intersectionObserver = null;
        this.animatedItems = new Set();
        
        this.init();
    }

    /**
     * Initialize benefits section
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupIntersectionObserver();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('CV Benefits initialized successfully');
        } catch (error) {
            console.error('Error initializing benefits:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.benefitsSection = document.querySelector('.cv-benefits-section');
        
        if (this.benefitsSection) {
            this.benefitItems = this.benefitsSection.querySelectorAll('.cv-benefit-item');
        }
    }

    /**
     * Setup intersection observer
     */
    setupIntersectionObserver() {
        const options = {
            root: null,
            rootMargin: '0px 0px -50px 0px',
            threshold: 0.1
        };

        this.intersectionObserver = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.animateBenefitItem(entry.target);
                }
            });
        }, options);

        // Observe all benefit items
        this.benefitItems.forEach(item => {
            this.intersectionObserver.observe(item);
        });
    }

    /**
     * Animate benefit item
     */
    animateBenefitItem(item) {
        if (this.animatedItems.has(item)) return;
        
        // Add animation classes
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = 'all 0.6s ease';
        
        // Trigger animation
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 100);
        
        this.animatedItems.add(item);
    }

    /**
     * Bind events
     */
    bindEvents() {
        if (!this.benefitsSection) return;

        // Add hover effects to benefit items
        this.benefitItems.forEach(item => {
            item.addEventListener('mouseenter', () => this.handleItemHover(item));
            item.addEventListener('mouseleave', () => this.handleItemLeave(item));
        });

        // Add click effects
        this.benefitItems.forEach(item => {
            item.addEventListener('click', () => this.handleItemClick(item));
        });
    }

    /**
     * Handle item hover
     */
    handleItemHover(item) {
        const icon = item.querySelector('.cv-benefit-icon');
        if (icon) {
            icon.style.transform = 'translateY(-2px) scale(1.05)';
            icon.style.boxShadow = '0 8px 20px rgba(74, 144, 226, 0.4)';
        }
    }

    /**
     * Handle item leave
     */
    handleItemLeave(item) {
        const icon = item.querySelector('.cv-benefit-icon');
        if (icon) {
            icon.style.transform = 'translateY(0) scale(1)';
            icon.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.4), 0 0 20px rgba(74, 144, 226, 0.3)';
        }
    }

    /**
     * Handle item click
     */
    handleItemClick(item) {
        // Add click animation
        item.style.transform = 'scale(0.98)';
        
        setTimeout(() => {
            item.style.transform = '';
        }, 150);
        
        // Log interaction for analytics
        const title = item.querySelector('.cv-benefit-content h5');
        if (title) {
            console.log('Benefit clicked:', title.textContent);
        }
    }

    /**
     * Animate benefits section on scroll
     */
    animateBenefitsOnScroll() {
        if (!this.benefitsSection) return;

        const scrolled = window.pageYOffset;
        const sectionTop = this.benefitsSection.offsetTop;
        const sectionHeight = this.benefitsSection.offsetHeight;
        const windowHeight = window.innerHeight;
        
        // Calculate scroll progress
        const progress = Math.min(
            Math.max((scrolled - sectionTop + windowHeight) / sectionHeight, 0),
            1
        );
        
        // Update overlay opacity
        const overlay = this.benefitsSection.querySelector('.cv-benefits-overlay');
        if (overlay) {
            overlay.style.opacity = 0.3 + (progress * 0.2);
        }
        
        // Update title animation
        const title = this.benefitsSection.querySelector('.cv-benefits-title');
        if (title) {
            const titleProgress = Math.min(progress * 2, 1);
            title.style.transform = `translateY(${20 * (1 - titleProgress)}px)`;
            title.style.opacity = titleProgress;
        }
    }

    /**
     * Setup scroll animations
     */
    setupScrollAnimations() {
        window.addEventListener('scroll', () => this.animateBenefitsOnScroll());
    }

    /**
     * Get benefits state
     */
    getBenefitsState() {
        return {
            isInitialized: this.isInitialized,
            itemsCount: this.benefitItems.length,
            animatedItems: this.animatedItems.size
        };
    }

    /**
     * Destroy benefits
     */
    destroy() {
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
        
        if (this.benefitsSection) {
            this.benefitItems.forEach(item => {
                item.removeEventListener('mouseenter', this.handleItemHover);
                item.removeEventListener('mouseleave', this.handleItemLeave);
                item.removeEventListener('click', this.handleItemClick);
            });
        }
        
        window.removeEventListener('scroll', this.animateBenefitsOnScroll);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.CVBenefits = CVBenefits;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.cvBenefits = new CVBenefits();
});
