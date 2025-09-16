/**
 * CONTACT HERO - HERO SECTION MANAGEMENT
 * =====================================
 * Handles the hero section with background and animations for the contact page
 */

class ContactHero {
    constructor() {
        this.heroSection = null;
        this.backgroundImage = null;
        this.isInitialized = false;
        this.parallaxEnabled = false;
        this.scrollHandler = null;
        
        this.init();
    }

    /**
     * Initialize hero section
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupParallax();
            this.bindEvents();
            this.setupAnimations();
            this.isInitialized = true;
            
            console.log('Contact Hero initialized successfully');
        } catch (error) {
            console.error('Error initializing hero section:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.heroSection = document.querySelector('.contact-hero-section');
        this.backgroundImage = this.heroSection?.style.backgroundImage;
    }

    /**
     * Setup parallax effect
     */
    setupParallax() {
        // Parallax is disabled by default for better performance
        // Can be enabled by setting this.parallaxEnabled = true
        if (this.parallaxEnabled) {
            this.scrollHandler = () => this.updateParallax();
            window.addEventListener('scroll', this.scrollHandler);
        }
    }

    /**
     * Update parallax effect
     */
    updateParallax() {
        if (!this.heroSection || !this.parallaxEnabled) return;

        const scrolled = window.pageYOffset;
        const rate = scrolled * -0.5;
        
        this.heroSection.style.transform = `translateY(${rate}px)`;
    }

    /**
     * Bind events
     */
    bindEvents() {
        // Window resize
        window.addEventListener('resize', () => this.handleResize());
        
        // Scroll events for animations
        window.addEventListener('scroll', () => this.handleScroll());
        
        // Page load
        window.addEventListener('load', () => this.handleLoad());
    }

    /**
     * Handle window resize
     */
    handleResize() {
        this.adjustBackgroundSize();
        this.updateAnimations();
    }

    /**
     * Handle scroll events
     */
    handleScroll() {
        this.updateAnimations();
    }

    /**
     * Handle page load
     */
    handleLoad() {
        this.animateHeroContent();
    }

    /**
     * Setup animations
     */
    setupAnimations() {
        if (!this.heroSection) return;

        // Add initial animation classes
        const title = this.heroSection.querySelector('.contact-hero-title');
        if (title) {
            title.style.opacity = '0';
            title.style.transform = 'translateY(30px)';
        }
    }

    /**
     * Animate hero content
     */
    animateHeroContent() {
        const title = this.heroSection?.querySelector('.contact-hero-title');
        if (!title) return;

        // Animate title
        title.style.transition = 'all 0.8s ease';
        title.style.opacity = '1';
        title.style.transform = 'translateY(0)';
    }

    /**
     * Update animations based on scroll
     */
    updateAnimations() {
        if (!this.heroSection) return;

        const scrolled = window.pageYOffset;
        const heroHeight = this.heroSection.offsetHeight;
        const progress = Math.min(scrolled / heroHeight, 1);
        
        // Update background opacity
        const overlay = this.heroSection.querySelector('.contact-hero-overlay');
        if (overlay) {
            overlay.style.opacity = 0.1 + (progress * 0.4);
        }
    }

    /**
     * Adjust background size for different screen sizes
     */
    adjustBackgroundSize() {
        if (!this.heroSection) return;

        const width = window.innerWidth;
        let backgroundSize = '120%';
        
        if (width <= 1200) {
            backgroundSize = '150%';
        } else if (width <= 992) {
            backgroundSize = '180%';
        } else if (width <= 768) {
            backgroundSize = '200%';
        } else if (width <= 576) {
            backgroundSize = '250%';
        } else if (width <= 480) {
            backgroundSize = '300%';
        }
        
        this.heroSection.style.backgroundSize = backgroundSize;
    }

    /**
     * Enable parallax effect
     */
    enableParallax() {
        this.parallaxEnabled = true;
        if (!this.scrollHandler) {
            this.scrollHandler = () => this.updateParallax();
            window.addEventListener('scroll', this.scrollHandler);
        }
    }

    /**
     * Disable parallax effect
     */
    disableParallax() {
        this.parallaxEnabled = false;
        if (this.scrollHandler) {
            window.removeEventListener('scroll', this.scrollHandler);
            this.scrollHandler = null;
        }
        
        if (this.heroSection) {
            this.heroSection.style.transform = '';
        }
    }

    /**
     * Set background image
     */
    setBackgroundImage(imageUrl) {
        if (this.heroSection) {
            this.heroSection.style.backgroundImage = `url('${imageUrl}')`;
            this.backgroundImage = imageUrl;
        }
    }

    /**
     * Get hero state
     */
    getHeroState() {
        return {
            isInitialized: this.isInitialized,
            parallaxEnabled: this.parallaxEnabled,
            backgroundImage: this.backgroundImage
        };
    }

    /**
     * Destroy hero section
     */
    destroy() {
        if (this.scrollHandler) {
            window.removeEventListener('scroll', this.scrollHandler);
            this.scrollHandler = null;
        }
        
        window.removeEventListener('resize', this.handleResize);
        window.removeEventListener('scroll', this.handleScroll);
        window.removeEventListener('load', this.handleLoad);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.ContactHero = ContactHero;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.contactHero = new ContactHero();
});
