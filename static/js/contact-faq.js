/**
 * CONTACT FAQ - FAQ MANAGEMENT
 * ============================
 * Handles the FAQ accordion functionality for the contact page
 */

class ContactFAQ {
    constructor() {
        this.accordion = null;
        this.items = [];
        this.isInitialized = false;
        this.activeItem = null;
        
        this.init();
    }

    /**
     * Initialize FAQ accordion
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.bindEvents();
            this.setupKeyboardNavigation();
            this.isInitialized = true;
            
            console.log('Contact FAQ initialized successfully');
        } catch (error) {
            console.error('Error initializing FAQ:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.accordion = document.getElementById('faqAccordion');
        
        if (this.accordion) {
            this.items = this.accordion.querySelectorAll('.contact-faq-item');
        }
    }

    /**
     * Bind events
     */
    bindEvents() {
        if (!this.accordion) return;

        this.items.forEach((item, index) => {
            const header = item.querySelector('.contact-faq-header');
            const body = item.querySelector('.contact-faq-body');
            
            if (header && body) {
                // Click event
                header.addEventListener('click', () => this.toggleItem(index));
                
                // Keyboard event
                header.addEventListener('keydown', (e) => this.handleKeyboard(e, index));
            }
        });
    }

    /**
     * Setup keyboard navigation
     */
    setupKeyboardNavigation() {
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                this.closeAllItems();
            }
        });
    }

    /**
     * Toggle FAQ item
     */
    toggleItem(index) {
        const item = this.items[index];
        if (!item) return;

        const header = item.querySelector('.contact-faq-header');
        const body = item.querySelector('.contact-faq-body');
        
        if (!header || !body) return;

        const isOpen = header.getAttribute('aria-expanded') === 'true';
        
        if (isOpen) {
            this.closeItem(index);
        } else {
            this.openItem(index);
        }
    }

    /**
     * Open FAQ item
     */
    openItem(index) {
        const item = this.items[index];
        if (!item) return;

        const header = item.querySelector('.contact-faq-header');
        const body = item.querySelector('.contact-faq-body');
        
        if (!header || !body) return;

        // Close other items if needed
        this.closeOtherItems(index);

        // Open current item
        header.setAttribute('aria-expanded', 'true');
        body.style.display = 'block';
        
        // Add animation
        this.animateOpen(body);
        
        this.activeItem = index;
    }

    /**
     * Close FAQ item
     */
    closeItem(index) {
        const item = this.items[index];
        if (!item) return;

        const header = item.querySelector('.contact-faq-header');
        const body = item.querySelector('.contact-faq-body');
        
        if (!header || !body) return;

        header.setAttribute('aria-expanded', 'false');
        
        // Add animation
        this.animateClose(body);
        
        if (this.activeItem === index) {
            this.activeItem = null;
        }
    }

    /**
     * Close other items
     */
    closeOtherItems(currentIndex) {
        this.items.forEach((item, index) => {
            if (index !== currentIndex) {
                this.closeItem(index);
            }
        });
    }

    /**
     * Close all items
     */
    closeAllItems() {
        this.items.forEach((item, index) => {
            this.closeItem(index);
        });
    }

    /**
     * Animate open
     */
    animateOpen(body) {
        body.style.maxHeight = '0';
        body.style.overflow = 'hidden';
        body.style.transition = 'max-height 0.3s ease';
        
        // Force reflow
        body.offsetHeight;
        
        body.style.maxHeight = body.scrollHeight + 'px';
        
        // Clean up after animation
        setTimeout(() => {
            body.style.maxHeight = '';
            body.style.overflow = '';
            body.style.transition = '';
        }, 300);
    }

    /**
     * Animate close
     */
    animateClose(body) {
        body.style.maxHeight = body.scrollHeight + 'px';
        body.style.overflow = 'hidden';
        body.style.transition = 'max-height 0.3s ease';
        
        // Force reflow
        body.offsetHeight;
        
        body.style.maxHeight = '0';
        
        // Hide after animation
        setTimeout(() => {
            body.style.display = 'none';
            body.style.maxHeight = '';
            body.style.overflow = '';
            body.style.transition = '';
        }, 300);
    }

    /**
     * Handle keyboard navigation
     */
    handleKeyboard(event, index) {
        switch (event.key) {
            case 'Enter':
            case ' ':
                event.preventDefault();
                this.toggleItem(index);
                break;
            case 'ArrowDown':
                event.preventDefault();
                this.focusNextItem(index);
                break;
            case 'ArrowUp':
                event.preventDefault();
                this.focusPreviousItem(index);
                break;
            case 'Home':
                event.preventDefault();
                this.focusFirstItem();
                break;
            case 'End':
                event.preventDefault();
                this.focusLastItem();
                break;
        }
    }

    /**
     * Focus next item
     */
    focusNextItem(currentIndex) {
        const nextIndex = (currentIndex + 1) % this.items.length;
        this.focusItem(nextIndex);
    }

    /**
     * Focus previous item
     */
    focusPreviousItem(currentIndex) {
        const prevIndex = currentIndex === 0 ? this.items.length - 1 : currentIndex - 1;
        this.focusItem(prevIndex);
    }

    /**
     * Focus first item
     */
    focusFirstItem() {
        this.focusItem(0);
    }

    /**
     * Focus last item
     */
    focusLastItem() {
        this.focusItem(this.items.length - 1);
    }

    /**
     * Focus specific item
     */
    focusItem(index) {
        const item = this.items[index];
        if (!item) return;

        const header = item.querySelector('.contact-faq-header');
        if (header) {
            header.focus();
        }
    }

    /**
     * Get active item
     */
    getActiveItem() {
        return this.activeItem;
    }

    /**
     * Get items count
     */
    getItemsCount() {
        return this.items.length;
    }

    /**
     * Get FAQ state
     */
    getFAQState() {
        return {
            isInitialized: this.isInitialized,
            itemsCount: this.getItemsCount(),
            activeItem: this.getActiveItem()
        };
    }

    /**
     * Destroy FAQ
     */
    destroy() {
        if (this.accordion) {
            this.items.forEach((item, index) => {
                const header = item.querySelector('.contact-faq-header');
                if (header) {
                    header.removeEventListener('click', () => this.toggleItem(index));
                    header.removeEventListener('keydown', (e) => this.handleKeyboard(e, index));
                }
            });
        }
        
        document.removeEventListener('keydown', this.handleKeyboard);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.ContactFAQ = ContactFAQ;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.contactFAQ = new ContactFAQ();
});
