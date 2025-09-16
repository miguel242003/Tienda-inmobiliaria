/**
 * BUSCAR PROPIEDADES HERO - HERO SECTION MANAGEMENT
 * ================================================
 * Handles the hero section with background carousel for the buscar propiedades page
 */

class BuscarPropiedadesHero {
    constructor() {
        this.carousel = null;
        this.images = [];
        this.currentImageIndex = 0;
        this.intervalId = null;
        this.isInitialized = false;
        this.intervalTime = 5000; // 5 seconds
        
        this.init();
    }

    /**
     * Initialize hero section
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupCarousel();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('Buscar Propiedades Hero initialized successfully');
        } catch (error) {
            console.error('Error initializing hero section:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.carousel = document.getElementById('backgroundCarousel');
        
        // Get images from data attributes or default
        this.images = [
            '/static/images/filtropropiedad.jpg',
            '/static/images/filtropropiedad2.jpg'
        ];
    }

    /**
     * Setup carousel functionality
     */
    setupCarousel() {
        if (!this.carousel) {
            console.warn('Hero carousel element not found');
            return;
        }

        // Set initial background
        if (this.images.length > 0) {
            this.carousel.style.backgroundImage = `url('${this.images[0]}')`;
        }

        // Start carousel if we have multiple images
        if (this.images.length > 1) {
            this.startCarousel();
        }
    }

    /**
     * Start carousel rotation
     */
    startCarousel() {
        this.intervalId = setInterval(() => {
            this.nextImage();
        }, this.intervalTime);
    }

    /**
     * Stop carousel rotation
     */
    stopCarousel() {
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }
    }

    /**
     * Go to next image
     */
    nextImage() {
        this.currentImageIndex = (this.currentImageIndex + 1) % this.images.length;
        this.changeBackgroundImage(this.images[this.currentImageIndex]);
    }

    /**
     * Go to previous image
     */
    previousImage() {
        this.currentImageIndex = this.currentImageIndex === 0 
            ? this.images.length - 1 
            : this.currentImageIndex - 1;
        this.changeBackgroundImage(this.images[this.currentImageIndex]);
    }

    /**
     * Change background image with transition
     */
    changeBackgroundImage(imageUrl) {
        if (!this.carousel) return;

        // Add fade effect
        this.carousel.style.opacity = '0.7';
        
        setTimeout(() => {
            this.carousel.style.backgroundImage = `url('${imageUrl}')`;
            this.carousel.style.opacity = '1';
        }, 300);
    }

    /**
     * Bind events
     */
    bindEvents() {
        // Pause carousel on hover
        if (this.carousel) {
            this.carousel.addEventListener('mouseenter', () => {
                this.stopCarousel();
            });

            this.carousel.addEventListener('mouseleave', () => {
                if (this.images.length > 1) {
                    this.startCarousel();
                }
            });
        }

        // Pause carousel when page is not visible
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.stopCarousel();
            } else if (this.images.length > 1) {
                this.startCarousel();
            }
        });

        // Pause carousel when window loses focus
        window.addEventListener('blur', () => {
            this.stopCarousel();
        });

        window.addEventListener('focus', () => {
            if (this.images.length > 1) {
                this.startCarousel();
            }
        });
    }

    /**
     * Add new image to carousel
     */
    addImage(imageUrl) {
        this.images.push(imageUrl);
        
        // Start carousel if we now have multiple images
        if (this.images.length > 1 && !this.intervalId) {
            this.startCarousel();
        }
    }

    /**
     * Remove image from carousel
     */
    removeImage(imageUrl) {
        const index = this.images.indexOf(imageUrl);
        if (index > -1) {
            this.images.splice(index, 1);
            
            // Stop carousel if we now have only one image
            if (this.images.length <= 1) {
                this.stopCarousel();
            }
        }
    }

    /**
     * Set carousel interval time
     */
    setIntervalTime(time) {
        this.intervalTime = time;
        
        // Restart carousel with new interval
        if (this.intervalId) {
            this.stopCarousel();
            this.startCarousel();
        }
    }

    /**
     * Get current image index
     */
    getCurrentImageIndex() {
        return this.currentImageIndex;
    }

    /**
     * Get total images count
     */
    getImagesCount() {
        return this.images.length;
    }

    /**
     * Get carousel state
     */
    getCarouselState() {
        return {
            isRunning: this.intervalId !== null,
            currentImage: this.currentImageIndex,
            totalImages: this.images.length,
            intervalTime: this.intervalTime
        };
    }

    /**
     * Destroy hero section
     */
    destroy() {
        this.stopCarousel();
        
        if (this.carousel) {
            this.carousel.removeEventListener('mouseenter', this.stopCarousel);
            this.carousel.removeEventListener('mouseleave', this.startCarousel);
        }
        
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        window.removeEventListener('blur', this.stopCarousel);
        window.removeEventListener('focus', this.startCarousel);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.BuscarPropiedadesHero = BuscarPropiedadesHero;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.buscarPropiedadesHero = new BuscarPropiedadesHero();
});
