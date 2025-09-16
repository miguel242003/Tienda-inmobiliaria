/**
 * LOGIN SECURITY - SECURITY MANAGEMENT
 * ====================================
 * Handles security features and monitoring for the login page
 */

class LoginSecurity {
    constructor() {
        this.isInitialized = false;
        this.securityFeatures = {};
        this.monitoring = {};
        this.sessionTimeout = 30 * 60 * 1000; // 30 minutes
        this.lastActivity = Date.now();
        
        this.init();
    }

    /**
     * Initialize security features
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.setupSecurityFeatures();
            this.bindEvents();
            this.startMonitoring();
            this.isInitialized = true;
            
            console.log('Login Security initialized successfully');
        } catch (error) {
            console.error('Error initializing login security:', error);
        }
    }

    /**
     * Setup security features
     */
    setupSecurityFeatures() {
        this.securityFeatures = {
            sessionTimeout: this.sessionTimeout,
            lastActivity: this.lastActivity,
            isSecure: this.checkSecureConnection(),
            userAgent: navigator.userAgent,
            screenResolution: `${screen.width}x${screen.height}`,
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            language: navigator.language
        };
    }

    /**
     * Check secure connection
     */
    checkSecureConnection() {
        return location.protocol === 'https:' || location.hostname === 'localhost';
    }

    /**
     * Bind events
     */
    bindEvents() {
        // Track user activity
        document.addEventListener('mousemove', () => this.updateActivity());
        document.addEventListener('keypress', () => this.updateActivity());
        document.addEventListener('click', () => this.updateActivity());
        document.addEventListener('scroll', () => this.updateActivity());
        
        // Track form interactions
        const form = document.getElementById('adminLoginForm');
        if (form) {
            form.addEventListener('input', () => this.trackFormInteraction());
            form.addEventListener('focus', () => this.trackFormFocus());
            form.addEventListener('blur', () => this.trackFormBlur());
        }
        
        // Track page visibility
        document.addEventListener('visibilitychange', () => this.handleVisibilityChange());
        
        // Track before unload
        window.addEventListener('beforeunload', () => this.handleBeforeUnload());
    }

    /**
     * Update activity timestamp
     */
    updateActivity() {
        this.lastActivity = Date.now();
        this.securityFeatures.lastActivity = this.lastActivity;
    }

    /**
     * Track form interaction
     */
    trackFormInteraction() {
        this.monitoring.formInteractions = (this.monitoring.formInteractions || 0) + 1;
        this.logSecurityEvent('form_interaction', {
            timestamp: new Date().toISOString(),
            interactions: this.monitoring.formInteractions
        });
    }

    /**
     * Track form focus
     */
    trackFormFocus() {
        this.monitoring.formFocusTime = Date.now();
        this.logSecurityEvent('form_focus', {
            timestamp: new Date().toISOString()
        });
    }

    /**
     * Track form blur
     */
    trackFormBlur() {
        if (this.monitoring.formFocusTime) {
            const focusDuration = Date.now() - this.monitoring.formFocusTime;
            this.logSecurityEvent('form_blur', {
                timestamp: new Date().toISOString(),
                focusDuration: focusDuration
            });
        }
    }

    /**
     * Handle visibility change
     */
    handleVisibilityChange() {
        if (document.hidden) {
            this.logSecurityEvent('page_hidden', {
                timestamp: new Date().toISOString()
            });
        } else {
            this.logSecurityEvent('page_visible', {
                timestamp: new Date().toISOString()
            });
        }
    }

    /**
     * Handle before unload
     */
    handleBeforeUnload() {
        this.logSecurityEvent('page_unload', {
            timestamp: new Date().toISOString(),
            sessionDuration: Date.now() - this.lastActivity
        });
    }

    /**
     * Start monitoring
     */
    startMonitoring() {
        // Check for session timeout
        setInterval(() => this.checkSessionTimeout(), 60000); // Check every minute
        
        // Monitor for suspicious activity
        setInterval(() => this.monitorSuspiciousActivity(), 5000); // Check every 5 seconds
        
        // Update security indicators
        setInterval(() => this.updateSecurityIndicators(), 10000); // Update every 10 seconds
    }

    /**
     * Check session timeout
     */
    checkSessionTimeout() {
        const timeSinceActivity = Date.now() - this.lastActivity;
        
        if (timeSinceActivity > this.sessionTimeout) {
            this.logSecurityEvent('session_timeout', {
                timestamp: new Date().toISOString(),
                timeSinceActivity: timeSinceActivity
            });
            
            this.showSessionTimeoutWarning();
        }
    }

    /**
     * Monitor suspicious activity
     */
    monitorSuspiciousActivity() {
        const currentTime = Date.now();
        const timeSinceActivity = currentTime - this.lastActivity;
        
        // Check for rapid form interactions
        if (this.monitoring.formInteractions > 10) {
            this.logSecurityEvent('suspicious_rapid_interactions', {
                timestamp: new Date().toISOString(),
                interactions: this.monitoring.formInteractions
            });
        }
        
        // Check for long idle time
        if (timeSinceActivity > 5 * 60 * 1000) { // 5 minutes
            this.logSecurityEvent('long_idle_time', {
                timestamp: new Date().toISOString(),
                idleTime: timeSinceActivity
            });
        }
    }

    /**
     * Update security indicators
     */
    updateSecurityIndicators() {
        const indicators = document.querySelectorAll('.login-security-icon');
        
        indicators.forEach((icon, index) => {
            // Add subtle animation to indicate active monitoring
            icon.style.transform = 'scale(1.05)';
            setTimeout(() => {
                icon.style.transform = 'scale(1)';
            }, 200);
        });
    }

    /**
     * Show session timeout warning
     */
    showSessionTimeoutWarning() {
        const warning = document.createElement('div');
        warning.className = 'login-alert alert-warning';
        warning.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <span>Sesión inactiva. Por seguridad, se cerrará automáticamente en 5 minutos.</span>
            <button class="login-alert-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        const form = document.getElementById('adminLoginForm');
        if (form) {
            form.parentNode.insertBefore(warning, form.nextSibling);
        }
    }

    /**
     * Log security event
     */
    logSecurityEvent(eventType, data) {
        const event = {
            type: eventType,
            timestamp: new Date().toISOString(),
            data: data,
            userAgent: this.securityFeatures.userAgent,
            screenResolution: this.securityFeatures.screenResolution,
            timezone: this.securityFeatures.timezone,
            language: this.securityFeatures.language,
            isSecure: this.securityFeatures.isSecure
        };
        
        // In production, this would be sent to a security monitoring service
        console.log('Security Event:', event);
        
        // Store in localStorage for debugging
        const events = JSON.parse(localStorage.getItem('securityEvents') || '[]');
        events.push(event);
        
        // Keep only last 100 events
        if (events.length > 100) {
            events.splice(0, events.length - 100);
        }
        
        localStorage.setItem('securityEvents', JSON.stringify(events));
    }

    /**
     * Get security status
     */
    getSecurityStatus() {
        return {
            isInitialized: this.isInitialized,
            isSecure: this.securityFeatures.isSecure,
            lastActivity: this.lastActivity,
            sessionTimeout: this.sessionTimeout,
            timeSinceActivity: Date.now() - this.lastActivity,
            monitoring: this.monitoring
        };
    }

    /**
     * Get security events
     */
    getSecurityEvents() {
        return JSON.parse(localStorage.getItem('securityEvents') || '[]');
    }

    /**
     * Clear security events
     */
    clearSecurityEvents() {
        localStorage.removeItem('securityEvents');
    }

    /**
     * Export security data
     */
    exportSecurityData() {
        const data = {
            securityFeatures: this.securityFeatures,
            monitoring: this.monitoring,
            events: this.getSecurityEvents(),
            exportTime: new Date().toISOString()
        };
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `security-data-${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);
    }

    /**
     * Destroy security
     */
    destroy() {
        document.removeEventListener('mousemove', this.updateActivity);
        document.removeEventListener('keypress', this.updateActivity);
        document.removeEventListener('click', this.updateActivity);
        document.removeEventListener('scroll', this.updateActivity);
        document.removeEventListener('visibilitychange', this.handleVisibilityChange);
        window.removeEventListener('beforeunload', this.handleBeforeUnload);
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.LoginSecurity = LoginSecurity;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.loginSecurity = new LoginSecurity();
});
