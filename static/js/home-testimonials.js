/**
 * HOME TESTIMONIALS - TESTIMONIALS CAROUSEL MANAGEMENT
 * =================================================
 * Handles the testimonials carousel functionality
 */

class HomeTestimonials {
    constructor() {
        this.track = null;
        this.items = [];
        this.prevBtn = null;
        this.nextBtn = null;
        this.currentPosition = 0;
        this.testimonialsPerView = 3;
        this.totalTestimonials = 0;
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Initialize testimonials carousel
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.calculateTestimonialsPerView();
            this.bindEvents();
            this.updateNavigationButtons();
            this.isInitialized = true;
            
            console.log('Home Testimonials initialized successfully');
        } catch (error) {
            console.error('Error initializing testimonials:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.track = document.getElementById('testimonialsTrack');
        this.items = document.querySelectorAll('.testimonial-item');
        this.prevBtn = document.getElementById('prevBtn');
        this.nextBtn = document.getElementById('nextBtn');
        this.totalTestimonials = this.items.length;
        
        // Validar que los elementos existan
        if (!this.track) {
            throw new Error('Testimonials track element not found');
        }
        
        if (this.items.length === 0) {
            throw new Error('No testimonial items found');
        }
    }

    /**
     * Calculate testimonials per view based on screen size
     */
    calculateTestimonialsPerView() {
        const width = window.innerWidth;
        
        if (width <= 575) {
            // Small mobile: 1 testimonial
            this.testimonialsPerView = 1;
        } else if (width <= 991) {
            // Tablet: 2 testimonials
            this.testimonialsPerView = 2;
        } else {
            // Desktop: 3 testimonials
            this.testimonialsPerView = 3;
        }
        
        // Reset position if necessary
        if (this.currentPosition > this.totalTestimonials - this.testimonialsPerView) {
            this.currentPosition = Math.max(0, this.totalTestimonials - this.testimonialsPerView);
            this.updateTestimonialsDisplay();
        }
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Navigation buttons
        if (this.prevBtn) {
            this.prevBtn.addEventListener('click', () => this.moveTestimonials('left'));
        }
        
        if (this.nextBtn) {
            this.nextBtn.addEventListener('click', () => this.moveTestimonials('right'));
        }

        // Window resize
        window.addEventListener('resize', () => this.handleResize());

        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    /**
     * Handle window resize
     */
    handleResize() {
        this.calculateTestimonialsPerView();
        this.updateNavigationButtons();
    }

    /**
     * Handle keyboard navigation
     */
    handleKeyboard(e) {
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            this.moveTestimonials('left');
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            this.moveTestimonials('right');
        }
    }

    /**
     * Move testimonials in specified direction
     */
    moveTestimonials(direction) {
        if (direction === 'right' && this.currentPosition < this.totalTestimonials - this.testimonialsPerView) {
            this.currentPosition++;
        } else if (direction === 'left' && this.currentPosition > 0) {
            this.currentPosition--;
        } else {
            return; // Can't move in this direction
        }
        
        this.updateTestimonialsDisplay();
        this.updateNavigationButtons();
    }

    /**
     * Update testimonials display
     */
    updateTestimonialsDisplay() {
        if (!this.track || this.items.length === 0) return;
        
        const itemWidth = this.items[0].offsetWidth;
        const gap = window.innerWidth <= 767 ? 16 : 32; // Smaller gap on mobile
        const totalItemWidth = itemWidth + gap;
        
        const translateX = -this.currentPosition * totalItemWidth;
        this.track.style.transform = `translateX(${translateX}px)`;
    }

    /**
     * Update navigation button states
     */
    updateNavigationButtons() {
        if (!this.prevBtn || !this.nextBtn) return;
        
        // Previous button
        if (this.currentPosition === 0) {
            this.prevBtn.disabled = true;
            this.prevBtn.style.opacity = '0.5';
        } else {
            this.prevBtn.disabled = false;
            this.prevBtn.style.opacity = '1';
        }
        
        // Next button
        if (this.currentPosition >= this.totalTestimonials - this.testimonialsPerView) {
            this.nextBtn.disabled = true;
            this.nextBtn.style.opacity = '0.5';
        } else {
            this.nextBtn.disabled = false;
            this.nextBtn.style.opacity = '1';
        }
    }

    /**
     * Go to specific position
     */
    goToPosition(position) {
        if (position < 0 || position > this.totalTestimonials - this.testimonialsPerView) return;
        
        this.currentPosition = position;
        this.updateTestimonialsDisplay();
        this.updateNavigationButtons();
    }

    /**
     * Get current position
     */
    getCurrentPosition() {
        return this.currentPosition;
    }

    /**
     * Get total testimonials
     */
    getTotalTestimonials() {
        return this.totalTestimonials;
    }

    /**
     * Get testimonials per view
     */
    getTestimonialsPerView() {
        return this.testimonialsPerView;
    }

    /**
     * Check if can move left
     */
    canMoveLeft() {
        return this.currentPosition > 0;
    }

    /**
     * Check if can move right
     */
    canMoveRight() {
        return this.currentPosition < this.totalTestimonials - this.testimonialsPerView;
    }

    /**
     * Refresh testimonials (useful when content changes)
     */
    refresh() {
        this.cacheElements();
        this.calculateTestimonialsPerView();
        this.updateNavigationButtons();
    }

    /**
     * Destroy testimonials carousel
     */
    destroy() {
        if (this.prevBtn) {
            this.prevBtn.removeEventListener('click', this.moveTestimonials);
        }
        
        if (this.nextBtn) {
            this.nextBtn.removeEventListener('click', this.moveTestimonials);
        }
        
        window.removeEventListener('resize', this.handleResize);
        document.removeEventListener('keydown', this.handleKeyboard);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.HomeTestimonials = HomeTestimonials;

// Auto-initialize when DOM is ready (only if testimonials elements exist)
document.addEventListener('DOMContentLoaded', () => {
    const testimonialsTrack = document.getElementById('testimonialsTrack');
    
    if (testimonialsTrack) {
        window.homeTestimonials = new HomeTestimonials();
        console.log('Home Testimonials auto-initialized');
    } else {
        console.log('Testimonials elements not found, skipping initialization');
    }
});
