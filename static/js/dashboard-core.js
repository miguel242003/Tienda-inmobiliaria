/**
 * DASHBOARD CORE - MODULAR JAVASCRIPT
 * ===================================
 * Core functionality for the admin dashboard
 */

class DashboardCore {
    constructor() {
        this.sidebar = null;
        this.sidebarToggle = null;
        this.sidebarOverlay = null;
        this.mainContent = null;
        this.currentSection = 'dashboard';
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Initialize the dashboard
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.bindEvents();
            this.setupResponsive();
            this.isInitialized = true;
            
            console.log('Dashboard Core initialized successfully');
        } catch (error) {
            console.error('Error initializing dashboard:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.sidebar = document.getElementById('sidebar');
        this.sidebarToggle = document.getElementById('sidebar-toggle');
        this.sidebarOverlay = document.getElementById('sidebar-overlay');
        this.mainContent = document.getElementById('main-content');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Sidebar toggle
        if (this.sidebarToggle) {
            this.sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // Sidebar overlay
        if (this.sidebarOverlay) {
            this.sidebarOverlay.addEventListener('click', () => this.closeSidebar());
        }

        // Window resize
        window.addEventListener('resize', () => this.handleResize());
        
        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
    }

    /**
     * Setup responsive behavior
     */
    setupResponsive() {
        this.handleResize();
    }

    /**
     * Toggle sidebar visibility
     */
    toggleSidebar() {
        if (!this.sidebar) return;
        
        const isOpen = this.sidebar.classList.contains('open');
        
        if (isOpen) {
            this.closeSidebar();
        } else {
            this.openSidebar();
        }
    }

    /**
     * Open sidebar
     */
    openSidebar() {
        if (!this.sidebar || !this.sidebarOverlay) return;
        
        this.sidebar.classList.add('open');
        this.sidebarOverlay.classList.add('active');
        this.mainContent?.classList.add('sidebar-open');
        
        // Prevent body scroll
        document.body.style.overflow = 'hidden';
    }

    /**
     * Close sidebar
     */
    closeSidebar() {
        if (!this.sidebar || !this.sidebarOverlay) return;
        
        this.sidebar.classList.remove('open');
        this.sidebarOverlay.classList.remove('active');
        this.mainContent?.classList.remove('sidebar-open');
        
        // Restore body scroll
        document.body.style.overflow = '';
    }

    /**
     * Handle window resize
     */
    handleResize() {
        if (window.innerWidth >= 1024) {
            this.closeSidebar();
        }
    }

    /**
     * Handle keyboard shortcuts
     */
    handleKeyboard(e) {
        // Escape key closes sidebar
        if (e.key === 'Escape') {
            this.closeSidebar();
        }
        
        // Ctrl/Cmd + B toggles sidebar
        if ((e.ctrlKey || e.metaKey) && e.key === 'b') {
            e.preventDefault();
            this.toggleSidebar();
        }
    }

    /**
     * Navigate to section
     */
    navigateTo(section) {
        this.hideAllSections();
        this.showSection(section);
        this.updateSidebarState(section);
        this.currentSection = section;
    }

    /**
     * Hide all content sections
     */
    hideAllSections() {
        const sections = document.querySelectorAll('.content-section');
        sections.forEach(section => section.classList.add('hidden'));
        
        // Also hide specific sections
        const specificSections = [
            'gestion-resenas-content',
            'gestion-propiedades-content',
            'configuraciones-content'
        ];
        
        specificSections.forEach(id => {
            const element = document.getElementById(id);
            if (element) {
                element.classList.add('hidden');
            }
        });
    }

    /**
     * Show specific section
     */
    showSection(section) {
        const sectionMap = {
            'dashboard': 'dashboard-content',
            'gestion': 'gestion-propiedades-content',
            'resenas': 'gestion-resenas-content',
            'configuraciones': 'configuraciones-content'
        };
        
        const sectionId = sectionMap[section];
        if (sectionId) {
            const element = document.getElementById(sectionId);
            if (element) {
                element.classList.remove('hidden');
            }
        }
    }

    /**
     * Update sidebar active state
     */
    updateSidebarState(activeSection) {
        // Remove active state from all buttons
        const buttons = document.querySelectorAll('#sidebar button, #sidebar a');
        buttons.forEach(btn => btn.classList.remove('bg-primary-100', 'text-primary-700'));
        
        // Add active state to current section
        const activeButton = document.querySelector(`[data-section="${activeSection}"]`);
        if (activeButton) {
            activeButton.classList.add('bg-primary-100', 'text-primary-700');
        }
    }

    /**
     * Show loading state
     */
    showLoading(element) {
        if (element) {
            element.classList.add('loading');
        }
    }

    /**
     * Hide loading state
     */
    hideLoading(element) {
        if (element) {
            element.classList.remove('loading');
        }
    }

    /**
     * Get current section
     */
    getCurrentSection() {
        return this.currentSection;
    }

    /**
     * Destroy instance
     */
    destroy() {
        // Remove event listeners
        if (this.sidebarToggle) {
            this.sidebarToggle.removeEventListener('click', this.toggleSidebar);
        }
        
        if (this.sidebarOverlay) {
            this.sidebarOverlay.removeEventListener('click', this.closeSidebar);
        }
        
        window.removeEventListener('resize', this.handleResize);
        document.removeEventListener('keydown', this.handleKeyboard);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.DashboardCore = DashboardCore;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardCore = new DashboardCore();
});
