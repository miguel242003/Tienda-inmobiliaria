/**
 * CONTACT FORM - FORM MANAGEMENT
 * =============================
 * Handles the contact form functionality and validation
 */

class ContactForm {
    constructor() {
        this.form = null;
        this.inputs = {};
        this.isInitialized = false;
        this.validationRules = {};
        this.isSubmitting = false;
        
        this.init();
    }

    /**
     * Initialize contact form
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupValidation();
            this.bindEvents();
            this.preselectAsunto();
            this.isInitialized = true;
            
            console.log('Contact Form initialized successfully');
        } catch (error) {
            console.error('Error initializing contact form:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.form = document.getElementById('contactForm');
        
        if (this.form) {
            this.inputs = {
                nombre: this.form.querySelector('#nombre'),
                email: this.form.querySelector('#email'),
                telefono: this.form.querySelector('#telefono'),
                asunto: this.form.querySelector('#asunto'),
                mensaje: this.form.querySelector('#mensaje')
            };
        }
    }

    /**
     * Setup validation rules
     */
    setupValidation() {
        this.validationRules = {
            nombre: {
                required: true,
                minLength: 2,
                message: 'El nombre debe tener al menos 2 caracteres'
            },
            email: {
                required: true,
                pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                message: 'Por favor ingresa un email válido'
            },
            telefono: {
                required: false,
                pattern: /^[\+]?[0-9\s\-\(\)]{10,}$/,
                message: 'Por favor ingresa un teléfono válido'
            },
            asunto: {
                required: true,
                message: 'Por favor selecciona un asunto'
            },
            mensaje: {
                required: true,
                minLength: 10,
                message: 'El mensaje debe tener al menos 10 caracteres'
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
    }

    /**
     * Handle form submission
     */
    handleSubmit(event) {
        event.preventDefault();
        
        if (this.isSubmitting) return;
        
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
            if (!this.validateInput({ target: this.inputs[key] }, key)) {
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
        input.classList.remove('is-invalid');
        
        const feedback = input.parentNode.querySelector('.contact-form-feedback');
        if (feedback) {
            feedback.textContent = '';
            feedback.style.display = 'none';
        }
    }

    /**
     * Show validation error
     */
    showValidationError(input, message) {
        input.classList.add('is-invalid');
        
        const feedback = input.parentNode.querySelector('.contact-form-feedback');
        if (feedback) {
            feedback.textContent = message;
            feedback.style.display = 'block';
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
            
            // Show success message
            this.showSuccessMessage();
            
            // Reset form
            this.resetForm();
            
        } catch (error) {
            console.error('Error submitting form:', error);
            this.showErrorMessage();
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
     * Set loading state
     */
    setLoadingState(loading) {
        const submitBtn = this.form.querySelector('.contact-cta-button');
        if (submitBtn) {
            if (loading) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
            } else {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar Mensaje';
            }
        }
    }

    /**
     * Show success message
     */
    showSuccessMessage() {
        if (window.mostrarNotificacion) {
            window.mostrarNotificacion('success', '¡Mensaje Enviado!', 'Gracias por tu mensaje. Te contactaremos pronto.');
        } else {
            alert('¡Mensaje enviado exitosamente!');
        }
    }

    /**
     * Show error message
     */
    showErrorMessage() {
        if (window.mostrarNotificacion) {
            window.mostrarNotificacion('error', 'Error al enviar', 'Hubo un problema al enviar tu mensaje. Por favor intenta de nuevo.');
        } else {
            alert('Error al enviar el mensaje. Por favor intenta de nuevo.');
        }
    }

    /**
     * Reset form
     */
    resetForm() {
        this.form.reset();
        
        // Clear all validations
        Object.values(this.inputs).forEach(input => {
            if (input) {
                input.classList.remove('is-invalid');
                const feedback = input.parentNode.querySelector('.contact-form-feedback');
                if (feedback) {
                    feedback.textContent = '';
                    feedback.style.display = 'none';
                }
            }
        });
    }

    /**
     * Preselect asunto from URL
     */
    preselectAsunto() {
        const urlParams = new URLSearchParams(window.location.search);
        const asunto = urlParams.get('asunto');
        
        if (asunto && this.inputs.asunto) {
            this.inputs.asunto.value = asunto;
        }
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
     * Set form data
     */
    setFormData(data) {
        Object.keys(data).forEach(key => {
            if (this.inputs[key]) {
                this.inputs[key].value = data[key];
            }
        });
    }

    /**
     * Get form state
     */
    getFormState() {
        return {
            isInitialized: this.isInitialized,
            isSubmitting: this.isSubmitting,
            formData: this.getFormData(),
            isValid: this.validateForm()
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
window.ContactForm = ContactForm;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.contactForm = new ContactForm();
});
