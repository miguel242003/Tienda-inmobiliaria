/**
 * ABOUT ANIMATIONS - ANIMATION MANAGEMENT
 * ======================================
 * Handles animations and scroll effects for the about page
 */

class AboutAnimations {
    constructor() {
        this.aboutSection = null;
        this.valueCards = [];
        this.aboutItems = [];
        this.isInitialized = false;
        this.intersectionObserver = null;
        this.animatedElements = new Set();
        
        this.init();
    }

    /**
     * Initialize animations
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupIntersectionObserver();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('About Animations initialized successfully');
        } catch (error) {
            console.error('Error initializing about animations:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.aboutSection = document.querySelector('.about-main-section');
        this.valueCards = document.querySelectorAll('.about-value-card');
        this.aboutItems = document.querySelectorAll('.about-item');
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
                    this.animateElement(entry.target);
                }
            });
        }, options);

        // Observe all elements
        this.aboutItems.forEach(item => {
            this.intersectionObserver.observe(item);
        });
        
        this.valueCards.forEach(card => {
            this.intersectionObserver.observe(card);
        });
    }

    /**
     * Animate element
     */
    animateElement(element) {
        if (this.animatedElements.has(element)) return;
        
        // Add animation classes based on element type
        if (element.classList.contains('about-item')) {
            this.animateAboutItem(element);
        } else if (element.classList.contains('about-value-card')) {
            this.animateValueCard(element);
        }
        
        this.animatedElements.add(element);
    }

    /**
     * Animate about item
     */
    animateAboutItem(item) {
        item.style.opacity = '0';
        item.style.transform = 'translateY(30px)';
        item.style.transition = 'all 0.6s ease';
        
        setTimeout(() => {
            item.style.opacity = '1';
            item.style.transform = 'translateY(0)';
        }, 100);
    }

    /**
     * Animate value card
     */
    animateValueCard(card) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(50px) scale(0.9)';
        card.style.transition = 'all 0.8s ease';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0) scale(1)';
        }, 200);
    }

    /**
     * Bind events
     */
    bindEvents() {
        // Add hover effects to value cards
        this.valueCards.forEach(card => {
            card.addEventListener('mouseenter', () => this.handleCardHover(card));
            card.addEventListener('mouseleave', () => this.handleCardLeave(card));
            card.addEventListener('click', () => this.handleCardClick(card));
        });

        // Add hover effects to about items
        this.aboutItems.forEach(item => {
            const icon = item.querySelector('.about-item-icon');
            if (icon) {
                icon.addEventListener('mouseenter', () => this.handleIconHover(icon));
                icon.addEventListener('mouseleave', () => this.handleIconLeave(icon));
            }
        });

        // Scroll animations
        window.addEventListener('scroll', () => this.handleScroll());
    }

    /**
     * Handle card hover
     */
    handleCardHover(card) {
        card.style.transform = 'translateY(-10px) scale(1.02)';
        card.style.boxShadow = '0 20px 40px rgba(0,0,0,.2)';
    }

    /**
     * Handle card leave
     */
    handleCardLeave(card) {
        // Reset to original position based on card index
        const index = Array.from(this.valueCards).indexOf(card);
        const originalY = this.getOriginalCardPosition(index);
        card.style.transform = `translateY(${originalY}px) scale(1)`;
        card.style.boxShadow = '0 12px 30px rgba(0,0,0,.12)';
    }

    /**
     * Handle card click
     */
    handleCardClick(card) {
        // Add click animation
        card.style.transform = 'scale(0.98)';
        
        setTimeout(() => {
            const index = Array.from(this.valueCards).indexOf(card);
            const originalY = this.getOriginalCardPosition(index);
            card.style.transform = `translateY(${originalY}px) scale(1)`;
        }, 150);
        
        // Log interaction for analytics
        const title = card.querySelector('.about-value-title');
        if (title) {
            console.log('Value card clicked:', title.textContent);
        }
    }

    /**
     * Handle icon hover
     */
    handleIconHover(icon) {
        icon.style.transform = 'scale(1.2) rotate(5deg)';
        icon.style.color = '#e67e22';
    }

    /**
     * Handle icon leave
     */
    handleIconLeave(icon) {
        icon.style.transform = 'scale(1) rotate(0deg)';
        icon.style.color = '#2c3e50';
    }

    /**
     * Get original card position
     */
    getOriginalCardPosition(index) {
        const positions = [160, 110, 160, 110];
        return positions[index] || 0;
    }

    /**
     * Handle scroll animations
     */
    handleScroll() {
        const scrolled = window.pageYOffset;
        const windowHeight = window.innerHeight;
        
        // Parallax effect for about section
        if (this.aboutSection) {
            const aboutTop = this.aboutSection.offsetTop;
            const aboutHeight = this.aboutSection.offsetHeight;
            const progress = Math.min(
                Math.max((scrolled - aboutTop + windowHeight) / aboutHeight, 0),
                1
            );
            
            // Update image transform
            const imageSection = this.aboutSection.querySelector('.about-image-section');
            if (imageSection) {
                const image = imageSection.querySelector('.about-image');
                if (image) {
                    const translateY = progress * 20;
                    image.style.transform = `translateY(${translateY}px)`;
                }
            }
        }
        
        // Stagger animation for value cards
        this.valueCards.forEach((card, index) => {
            const cardTop = card.offsetTop;
            const cardHeight = card.offsetHeight;
            const cardProgress = Math.min(
                Math.max((scrolled - cardTop + windowHeight) / cardHeight, 0),
                1
            );
            
            if (cardProgress > 0.3 && !this.animatedElements.has(card)) {
                this.animateValueCard(card);
                this.animatedElements.add(card);
            }
        });
    }

    /**
     * Animate about section on load
     */
    animateAboutSection() {
        if (!this.aboutSection) return;
        
        const content = this.aboutSection.querySelector('.about-content');
        if (content) {
            content.style.opacity = '0';
            content.style.transform = 'translateX(-30px)';
            content.style.transition = 'all 0.8s ease';
            
            setTimeout(() => {
                content.style.opacity = '1';
                content.style.transform = 'translateX(0)';
            }, 200);
        }
    }

    /**
     * Animate values section on load
     */
    animateValuesSection() {
        const valuesSection = document.querySelector('.about-values-hero');
        if (!valuesSection) return;
        
        const title = valuesSection.querySelector('.about-values-title');
        if (title) {
            title.style.opacity = '0';
            title.style.transform = 'translateY(-20px)';
            title.style.transition = 'all 0.6s ease';
            
            setTimeout(() => {
                title.style.opacity = '1';
                title.style.transform = 'translateY(0)';
            }, 100);
        }
    }

    /**
     * Get animation state
     */
    getAnimationState() {
        return {
            isInitialized: this.isInitialized,
            animatedElements: this.animatedElements.size,
            totalElements: this.aboutItems.length + this.valueCards.length
        };
    }

    /**
     * Destroy animations
     */
    destroy() {
        if (this.intersectionObserver) {
            this.intersectionObserver.disconnect();
        }
        
        if (this.valueCards.length > 0) {
            this.valueCards.forEach(card => {
                card.removeEventListener('mouseenter', this.handleCardHover);
                card.removeEventListener('mouseleave', this.handleCardLeave);
                card.removeEventListener('click', this.handleCardClick);
            });
        }
        
        if (this.aboutItems.length > 0) {
            this.aboutItems.forEach(item => {
                const icon = item.querySelector('.about-item-icon');
                if (icon) {
                    icon.removeEventListener('mouseenter', this.handleIconHover);
                    icon.removeEventListener('mouseleave', this.handleIconLeave);
                }
            });
        }
        
        window.removeEventListener('scroll', this.handleScroll);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.AboutAnimations = AboutAnimations;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.aboutAnimations = new AboutAnimations();
});
