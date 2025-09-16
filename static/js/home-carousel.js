/**
 * HOME CAROUSEL - HERO CAROUSEL MANAGEMENT
 * ======================================
 * Handles the hero carousel functionality
 */

class HomeCarousel {
    constructor() {
        this.carousel = null;
        this.items = [];
        this.indicators = [];
        this.currentIndex = 0;
        this.autoPlayInterval = null;
        this.autoPlayDelay = 5000; // 5 seconds
        this.isPlaying = true;
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Initialize carousel
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.carousel = document.getElementById('heroCarousel');
            if (!this.carousel) return;
            
            this.cacheElements();
            this.bindEvents();
            this.startAutoPlay();
            this.isInitialized = true;
            
            console.log('Home Carousel initialized successfully');
        } catch (error) {
            console.error('Error initializing carousel:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.items = this.carousel.querySelectorAll('.carousel-item');
        this.indicators = this.carousel.querySelectorAll('.indicator');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Indicator clicks
        this.indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => this.goToSlide(index));
        });

        // Pause on hover
        this.carousel.addEventListener('mouseenter', () => this.pauseAutoPlay());
        this.carousel.addEventListener('mouseleave', () => this.resumeAutoPlay());

        // Keyboard navigation
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));

        // Touch/swipe support
        this.addTouchSupport();
    }

    /**
     * Add touch/swipe support
     */
    addTouchSupport() {
        let startX = 0;
        let startY = 0;
        let endX = 0;
        let endY = 0;

        this.carousel.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });

        this.carousel.addEventListener('touchend', (e) => {
            endX = e.changedTouches[0].clientX;
            endY = e.changedTouches[0].clientY;
            this.handleSwipe(startX, startY, endX, endY);
        });
    }

    /**
     * Handle swipe gestures
     */
    handleSwipe(startX, startY, endX, endY) {
        const deltaX = endX - startX;
        const deltaY = endY - startY;
        const minSwipeDistance = 50;

        // Check if horizontal swipe is more significant than vertical
        if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > minSwipeDistance) {
            if (deltaX > 0) {
                this.previousSlide();
            } else {
                this.nextSlide();
            }
        }
    }

    /**
     * Handle keyboard navigation
     */
    handleKeyboard(e) {
        if (e.key === 'ArrowLeft') {
            e.preventDefault();
            this.previousSlide();
        } else if (e.key === 'ArrowRight') {
            e.preventDefault();
            this.nextSlide();
        }
    }

    /**
     * Go to specific slide
     */
    goToSlide(index) {
        if (index < 0 || index >= this.items.length) return;
        
        this.currentIndex = index;
        this.updateCarousel();
        this.updateIndicators();
        this.resetAutoPlay();
    }

    /**
     * Go to next slide
     */
    nextSlide() {
        this.currentIndex = (this.currentIndex + 1) % this.items.length;
        this.updateCarousel();
        this.updateIndicators();
        this.resetAutoPlay();
    }

    /**
     * Go to previous slide
     */
    previousSlide() {
        this.currentIndex = (this.currentIndex - 1 + this.items.length) % this.items.length;
        this.updateCarousel();
        this.updateIndicators();
        this.resetAutoPlay();
    }

    /**
     * Update carousel display
     */
    updateCarousel() {
        this.items.forEach((item, index) => {
            item.classList.toggle('active', index === this.currentIndex);
        });
    }

    /**
     * Update indicator states
     */
    updateIndicators() {
        this.indicators.forEach((indicator, index) => {
            indicator.classList.toggle('active', index === this.currentIndex);
        });
    }

    /**
     * Start auto-play
     */
    startAutoPlay() {
        if (this.autoPlayInterval) return;
        
        this.autoPlayInterval = setInterval(() => {
            if (this.isPlaying) {
                this.nextSlide();
            }
        }, this.autoPlayDelay);
    }

    /**
     * Stop auto-play
     */
    stopAutoPlay() {
        if (this.autoPlayInterval) {
            clearInterval(this.autoPlayInterval);
            this.autoPlayInterval = null;
        }
    }

    /**
     * Pause auto-play
     */
    pauseAutoPlay() {
        this.isPlaying = false;
    }

    /**
     * Resume auto-play
     */
    resumeAutoPlay() {
        this.isPlaying = true;
    }

    /**
     * Reset auto-play timer
     */
    resetAutoPlay() {
        this.stopAutoPlay();
        this.startAutoPlay();
    }

    /**
     * Get current slide index
     */
    getCurrentIndex() {
        return this.currentIndex;
    }

    /**
     * Get total slides
     */
    getTotalSlides() {
        return this.items.length;
    }

    /**
     * Destroy carousel
     */
    destroy() {
        this.stopAutoPlay();
        
        // Remove event listeners
        this.indicators.forEach(indicator => {
            indicator.removeEventListener('click', this.goToSlide);
        });
        
        this.carousel.removeEventListener('mouseenter', this.pauseAutoPlay);
        this.carousel.removeEventListener('mouseleave', this.resumeAutoPlay);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.HomeCarousel = HomeCarousel;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.homeCarousel = new HomeCarousel();
});
