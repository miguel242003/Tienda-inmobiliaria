/**
 * LOGIN FORM - FORM MANAGEMENT
 * ============================
 * Handles the login form functionality and validation
 */

class LoginForm {
    constructor() {
        this.form = null;
        this.inputs = {};
        this.isInitialized = false;
        this.validationRules = {};
        this.isSubmitting = false;
        this.attempts = 0;
        this.maxAttempts = 5;
        this.lockoutTime = 15 * 60 * 1000; // 15 minutes
        this.lockoutEnd = null;
        
        this.init();
    }

    /**
     * Initialize login form
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupValidation();
            this.bindEvents();
            this.checkLockout();
            this.isInitialized = true;
            
            console.log('Login Form initialized successfully');
        } catch (error) {
            console.error('Error initializing login form:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.form = document.getElementById('adminLoginForm');
        
        if (this.form) {
            this.inputs = {
                email: this.form.querySelector('#email'),
                password: this.form.querySelector('#password'),
                rememberMe: this.form.querySelector('#rememberMe')
            };
        }
    }

    /**
     * Setup validation rules
     */
    setupValidation() {
        this.validationRules = {
            email: {
                required: true,
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Por favor ingresa un correo electrónico válido'
            },
            password: {
                required: true,
                minLength: 6,
                message: 'La contraseña debe tener al menos 6 caracteres'
            }
        };
    }

    /**
     * Bind events
     */
    bindEvents() {
        if (!this.form) return;

        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // Real-time validation
        Object.keys(this.inputs).forEach(key => {
            const input = this.inputs[key];
            if (input) {
                input.addEventListener('blur', (e) => this.validateInput(e, key));
                input.addEventListener('input', (e) => this.clearValidation(e, key));
            }
        });

        // Password toggle
        const togglePassword = document.getElementById('togglePassword');
        if (togglePassword) {
            togglePassword.addEventListener('click', () => this.togglePasswordVisibility());
        }

        // Auto-focus on email field
        if (this.inputs.email) {
            this.inputs.email.focus();
        }
    }

    /**
     * Handle form submission
     */
    handleSubmit(event) {
        event.preventDefault();
        
        if (this.isSubmitting) return;
        
        // Check if account is locked
        if (this.isLocked()) {
            this.showLockoutMessage();
            return;
        }
        
        if (this.validateForm()) {
            this.submitForm();
        }
    }

    /**
     * Validate entire form
     */
    validateForm() {
        let isValid = true;
        
        Object.keys(this.inputs).forEach(key => {
            if (key !== 'rememberMe' && !this.validateInput({ target: this.inputs[key] }, key)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    /**
     * Validate individual input
     */
    validateInput(event, inputName) {
        const input = event.target;
        const value = input.value.trim();
        const rule = this.validationRules[inputName];
        
        if (!rule) return true;
        
        // Clear previous validation
        this.clearValidation(event, inputName);
        
        // Check required
        if (rule.required && !value) {
            this.showValidationError(input, 'Este campo es obligatorio');
            return false;
        }
        
        // Skip other validations if not required and empty
        if (!rule.required && !value) {
            return true;
        }
        
        // Check minimum length
        if (rule.minLength && value.length < rule.minLength) {
            this.showValidationError(input, rule.message);
            return false;
        }
        
        // Check pattern
        if (rule.pattern && !rule.pattern.test(value)) {
            this.showValidationError(input, rule.message);
            return false;
        }
        
        return true;
    }

    /**
     * Clear validation
     */
    clearValidation(event, inputName) {
        const input = event.target;
        input.classList.remove('is-invalid', 'is-valid');
    }

    /**
     * Show validation error
     */
    showValidationError(input, message) {
        input.classList.add('is-invalid');
        input.classList.remove('is-valid');
        
        // Show error message
        this.showMessage('error', message);
    }

    /**
     * Show validation success
     */
    showValidationSuccess(input) {
        input.classList.add('is-valid');
        input.classList.remove('is-invalid');
    }

    /**
     * Toggle password visibility
     */
    togglePasswordVisibility() {
        const passwordInput = this.inputs.password;
        const eyeIcon = document.getElementById('eyeIcon');
        
        if (passwordInput && eyeIcon) {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                eyeIcon.classList.remove('fa-eye');
                eyeIcon.classList.add('fa-eye-slash');
            } else {
                passwordInput.type = 'password';
                eyeIcon.classList.remove('fa-eye-slash');
                eyeIcon.classList.add('fa-eye');
            }
        }
    }

    /**
     * Submit form
     */
    async submitForm() {
        this.isSubmitting = true;
        this.setLoadingState(true);
        
        try {
            // Simulate form submission
            await this.simulateSubmission();
            
            // Check if login was successful (simulate)
            const isSuccess = this.simulateLoginSuccess();
            
            if (isSuccess) {
                this.handleLoginSuccess();
            } else {
                this.handleLoginFailure();
            }
            
        } catch (error) {
            console.error('Error submitting form:', error);
            this.handleLoginError();
        } finally {
            this.isSubmitting = false;
            this.setLoadingState(false);
        }
    }

    /**
     * Simulate form submission
     */
    simulateSubmission() {
        return new Promise((resolve) => {
            setTimeout(resolve, 2000);
        });
    }

    /**
     * Simulate login success (for demo purposes)
     */
    simulateLoginSuccess() {
        // In real implementation, this would be determined by server response
        const email = this.inputs.email.value;
        const password = this.inputs.password.value;
        
        // Simple demo logic
        return email === 'admin@example.com' && password === 'admin123';
    }

    /**
     * Handle login success
     */
    handleLoginSuccess() {
        this.showMessage('success', '¡Login exitoso! Redirigiendo...');
        this.resetAttempts();
        
        // Redirect to dashboard
        setTimeout(() => {
            window.location.href = '/dashboard/';
        }, 1500);
    }

    /**
     * Handle login failure
     */
    handleLoginFailure() {
        this.attempts++;
        this.showMessage('error', 'Credenciales incorrectas. Intento ' + this.attempts + ' de ' + this.maxAttempts);
        
        if (this.attempts >= this.maxAttempts) {
            this.lockAccount();
        }
    }

    /**
     * Handle login error
     */
    handleLoginError() {
        this.showMessage('error', 'Error al procesar el login. Por favor intenta de nuevo.');
    }

    /**
     * Set loading state
     */
    setLoadingState(loading) {
        const submitBtn = this.form.querySelector('.login-submit-btn');
        if (submitBtn) {
            if (loading) {
                submitBtn.disabled = true;
                submitBtn.classList.add('loading');
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Iniciando sesión...';
            } else {
                submitBtn.disabled = false;
                submitBtn.classList.remove('loading');
                submitBtn.innerHTML = '<i class="fas fa-sign-in-alt"></i> Iniciar Sesión';
            }
        }
    }

    /**
     * Show message
     */
    showMessage(type, message) {
        // Remove existing alerts
        const existingAlerts = document.querySelectorAll('.login-alert');
        existingAlerts.forEach(alert => alert.remove());
        
        // Create new alert
        const alert = document.createElement('div');
        alert.className = `login-alert alert-${type}`;
        alert.innerHTML = `
            <i class="fas fa-${this.getAlertIcon(type)}"></i>
            <span>${message}</span>
            <button class="login-alert-close" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        
        // Insert after form
        this.form.parentNode.insertBefore(alert, this.form.nextSibling);
        
        // Auto-remove after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    /**
     * Get alert icon
     */
    getAlertIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    /**
     * Check if account is locked
     */
    isLocked() {
        if (!this.lockoutEnd) return false;
        return Date.now() < this.lockoutEnd;
    }

    /**
     * Lock account
     */
    lockAccount() {
        this.lockoutEnd = Date.now() + this.lockoutTime;
        localStorage.setItem('loginLockout', this.lockoutEnd.toString());
        this.showLockoutMessage();
    }

    /**
     * Check lockout from localStorage
     */
    checkLockout() {
        const storedLockout = localStorage.getItem('loginLockout');
        if (storedLockout) {
            this.lockoutEnd = parseInt(storedLockout);
            if (this.isLocked()) {
                this.showLockoutMessage();
            } else {
                localStorage.removeItem('loginLockout');
                this.lockoutEnd = null;
            }
        }
    }

    /**
     * Show lockout message
     */
    showLockoutMessage() {
        const remainingTime = Math.ceil((this.lockoutEnd - Date.now()) / 1000 / 60);
        this.showMessage('error', `Cuenta bloqueada. Intenta de nuevo en ${remainingTime} minutos.`);
    }

    /**
     * Reset attempts
     */
    resetAttempts() {
        this.attempts = 0;
        this.lockoutEnd = null;
        localStorage.removeItem('loginLockout');
    }

    /**
     * Get form data
     */
    getFormData() {
        const formData = new FormData(this.form);
        const data = {};
        
        for (let [key, value] of formData.entries()) {
            data[key] = value;
        }
        
        return data;
    }

    /**
     * Get form state
     */
    getFormState() {
        return {
            isInitialized: this.isInitialized,
            isSubmitting: this.isSubmitting,
            attempts: this.attempts,
            isLocked: this.isLocked(),
            formData: this.getFormData()
        };
    }

    /**
     * Destroy form
     */
    destroy() {
        if (this.form) {
            this.form.removeEventListener('submit', this.handleSubmit);
            
            Object.values(this.inputs).forEach(input => {
                if (input) {
                    input.removeEventListener('blur', this.validateInput);
                    input.removeEventListener('input', this.clearValidation);
                }
            });
        }
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.LoginForm = LoginForm;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.loginForm = new LoginForm();
});
