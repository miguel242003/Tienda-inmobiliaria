/**
 * CONSORCIO ANIMATIONS - ANIMATION MANAGEMENT
 * ==========================================
 * Handles animations and visual effects for the consorcio page
 */

class ConsorcioAnimations {
    constructor() {
        this.animatedElements = [];
        this.intersectionObserver = null;
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Initialize animations
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.setupIntersectionObserver();
            this.observeElements();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('Consorcio Animations initialized successfully');
        } catch (error) {
            console.error('Error initializing animations:', error);
        }
    }

    /**
     * Setup intersection observer for scroll animations
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
                    this.animateElement(entry.target);
                }
            });
        }, options);
    }

    /**
     * Observe elements for animation
     */
    observeElements() {
        // Observe benefit items
        const benefitItems = document.querySelectorAll('.benefit-item');
        benefitItems.forEach((item, index) => {
            item.style.opacity = '0';
            item.style.transform = 'translateY(30px)';
            item.style.transition = `all 0.6s ease ${index * 0.1}s`;
            this.intersectionObserver.observe(item);
        });

        // Observe process steps
        const processSteps = document.querySelectorAll('.process-step');
        processSteps.forEach((step, index) => {
            step.style.opacity = '0';
            step.style.transform = 'translateX(-30px)';
            step.style.transition = `all 0.6s ease ${index * 0.1}s`;
            this.intersectionObserver.observe(step);
        });

        // Observe budget container
        const budgetContainer = document.querySelector('.consorcio-budget-container');
        if (budgetContainer) {
            budgetContainer.style.opacity = '0';
            budgetContainer.style.transform = 'translateX(30px)';
            budgetContainer.style.transition = 'all 0.6s ease';
            this.intersectionObserver.observe(budgetContainer);
        }

        // Observe main content
        const mainContent = document.querySelector('.consorcio-main-container');
        if (mainContent) {
            mainContent.style.opacity = '0';
            mainContent.style.transform = 'translateY(30px)';
            mainContent.style.transition = 'all 0.8s ease';
            this.intersectionObserver.observe(mainContent);
        }
    }

    /**
     * Animate element
     */
    animateElement(element) {
        element.style.opacity = '1';
        element.style.transform = 'translateY(0) translateX(0)';
        
        // Add animation class for additional effects
        element.classList.add('animate-fade-in');
    }

    /**
     * Bind events
     */
    bindEvents() {
        // Animate on scroll
        window.addEventListener('scroll', () => this.handleScroll());
        
        // Animate on page load
        window.addEventListener('load', () => this.handlePageLoad());
    }

    /**
     * Handle scroll events
     */
    handleScroll() {
        // Add parallax effect to background
        this.updateParallax();
        
        // Add scroll-based animations
        this.updateScrollAnimations();
    }

    /**
     * Handle page load
     */
    handlePageLoad() {
        // Animate hero section on load
        this.animateHeroSection();
    }

    /**
     * Update parallax effect
     */
    updateParallax() {
        const scrolled = window.pageYOffset;
        const parallaxElements = document.querySelectorAll('.consorcio-background');
        
        parallaxElements.forEach(element => {
            const speed = 0.5;
            element.style.transform = `translateY(${scrolled * speed}px)`;
        });
    }

    /**
     * Update scroll animations
     */
    updateScrollAnimations() {
        const scrolled = window.pageYOffset;
        const windowHeight = window.innerHeight;
        
        // Animate social icons based on scroll
        const socialIcons = document.querySelectorAll('.social-icon-optimal');
        socialIcons.forEach((icon, index) => {
            const delay = index * 0.1;
            if (scrolled > 100) {
                icon.style.transform = `scale(1.1) rotate(${scrolled * 0.1}deg)`;
            } else {
                icon.style.transform = 'scale(1) rotate(0deg)';
            }
        });
    }

    /**
     * Animate hero section
     */
    animateHeroSection() {
        const heroContent = document.querySelector('.consorcio-content');
        if (heroContent) {
            heroContent.style.opacity = '0';
            heroContent.style.transform = 'translateY(50px)';
            heroContent.style.transition = 'all 1s ease';
            
            setTimeout(() => {
                heroContent.style.opacity = '1';
                heroContent.style.transform = 'translateY(0)';
            }, 200);
        }
    }

    /**
     * Animate benefit items on hover
     */
    animateBenefitHover() {
        const benefitItems = document.querySelectorAll('.benefit-item');
        
        benefitItems.forEach(item => {
            item.addEventListener('mouseenter', () => {
                item.style.transform = 'translateY(-5px) scale(1.02)';
                item.style.boxShadow = '0 10px 25px rgba(43, 85, 162, 0.2)';
            });
            
            item.addEventListener('mouseleave', () => {
                item.style.transform = 'translateY(0) scale(1)';
                item.style.boxShadow = '0 2px 8px rgba(43, 85, 162, 0.1)';
            });
        });
    }

    /**
     * Animate process steps
     */
    animateProcessSteps() {
        const processSteps = document.querySelectorAll('.process-step');
        
        processSteps.forEach((step, index) => {
            step.addEventListener('mouseenter', () => {
                const number = step.querySelector('.process-step-number');
                if (number) {
                    number.style.transform = 'scale(1.2) rotate(360deg)';
                    number.style.transition = 'all 0.3s ease';
                }
            });
            
            step.addEventListener('mouseleave', () => {
                const number = step.querySelector('.process-step-number');
                if (number) {
                    number.style.transform = 'scale(1) rotate(0deg)';
                }
            });
        });
    }

    /**
     * Animate budget button
     */
    animateBudgetButton() {
        const budgetBtn = document.querySelector('.consorcio-budget-btn');
        if (budgetBtn) {
            budgetBtn.addEventListener('mouseenter', () => {
                budgetBtn.style.transform = 'translateY(-3px) scale(1.05)';
                budgetBtn.style.boxShadow = '0 8px 25px rgba(43, 85, 162, 0.4)';
            });
            
            budgetBtn.addEventListener('mouseleave', () => {
                budgetBtn.style.transform = 'translateY(0) scale(1)';
                budgetBtn.style.boxShadow = '0 4px 15px rgba(43, 85, 162, 0.3)';
            });
        }
    }

    /**
     * Setup all hover animations
     */
    setupHoverAnimations() {
        this.animateBenefitHover();
        this.animateProcessSteps();
        this.animateBudgetButton();
    }

    /**
     * Get animation state
     */
    getAnimationState() {
        return {
            isInitialized: this.isInitialized,
            observedElements: this.animatedElements.length
        };
    }

    /**
     * Destroy animations
     */
    destroy() {
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
        
        window.removeEventListener('scroll', this.handleScroll);
        window.removeEventListener('load', this.handlePageLoad);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.ConsorcioAnimations = ConsorcioAnimations;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.consorcioAnimations = new ConsorcioAnimations();
});
