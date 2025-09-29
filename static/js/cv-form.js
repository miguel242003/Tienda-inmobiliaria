/**
 * CV FORM - FORM MANAGEMENT
 * =========================
 * Handles the CV form functionality and validation
 */

class CVForm {
    constructor() {
        this.form = null;
        this.inputs = {};
        this.isInitialized = false;
        this.validationRules = {};
        this.isSubmitting = false;
        this.maxFileSize = 5 * 1024 * 1024; // 5MB
        this.allowedFileTypes = [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ];
        
        this.init();
    }

    /**
     * Initialize CV form
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupValidation();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('CV Form initialized successfully');
        } catch (error) {
            console.error('Error initializing CV form:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.form = document.getElementById('cvForm');
        
        if (this.form) {
            this.inputs = {
                nombre: this.form.querySelector('#nombre'),
                email: this.form.querySelector('#email'),
                telefono: this.form.querySelector('#telefono'),
                posicion: this.form.querySelector('#posicion'),
                experiencia: this.form.querySelector('#experiencia'),
                educacion: this.form.querySelector('#educacion'),
                cv_file: this.form.querySelector('#cv_file'),
                carta_presentacion: this.form.querySelector('#carta_presentacion')
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
                required: true,
                pattern: /^[\+]?[0-9\s\-\(\)]{8,15}$/,
                message: 'El teléfono es obligatorio y debe tener entre 8-15 dígitos'
            },
            posicion: {
                required: true,
                message: 'Por favor selecciona una posición'
            },
            experiencia: {
                required: false,
                message: 'Por favor selecciona tu experiencia'
            },
            educacion: {
                required: false,
                message: 'Por favor selecciona tu nivel educativo'
            },
            cv_file: {
                required: true,
                message: 'Por favor selecciona un archivo CV'
            },
            carta_presentacion: {
                required: false,
                maxLength: 500,
                message: 'La carta de presentación no puede exceder 500 caracteres'
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

        // Special handling for file input
        if (this.inputs.cv_file) {
            this.inputs.cv_file.addEventListener('change', (e) => this.handleFileChange(e));
        }
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
        
        // Check maximum length
        if (rule.maxLength && value.length > rule.maxLength) {
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
     * Handle file change
     */
    handleFileChange(event) {
        const input = event.target;
        const file = input.files[0];
        
        this.clearValidation(event, 'cv_file');
        
        if (file) {
            // Validate file size
            if (file.size > this.maxFileSize) {
                this.showValidationError(input, 'El archivo no puede ser mayor a 5MB');
                return false;
            }
            
            // Validate file type
            if (!this.allowedFileTypes.includes(file.type)) {
                this.showValidationError(input, 'Solo se permiten archivos PDF, DOC o DOCX');
                return false;
            }
        }
        
        return true;
    }

    /**
     * Clear validation
     */
    clearValidation(event, inputName) {
        const input = event.target;
        input.classList.remove('is-invalid');
        
        const feedback = input.parentNode.querySelector('.invalid-feedback');
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
        
        const feedback = input.parentNode.querySelector('.invalid-feedback');
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
        const submitBtn = this.form.querySelector('.btn-cta');
        if (submitBtn) {
            if (loading) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Enviando...';
            } else {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Enviar CV';
            }
        }
    }

    /**
     * Show success message
     */
    showSuccessMessage() {
        if (window.mostrarNotificacion) {
            window.mostrarNotificacion('success', '¡CV Enviado!', 'Gracias por enviar tu CV. Te contactaremos pronto si tu perfil coincide con nuestras necesidades.');
        } else {
            alert('¡CV enviado exitosamente!');
        }
    }

    /**
     * Show error message
     */
    showErrorMessage() {
        if (window.mostrarNotificacion) {
            window.mostrarNotificacion('error', 'Error al enviar', 'Hubo un problema al enviar tu CV. Por favor intenta de nuevo.');
        } else {
            alert('Error al enviar el CV. Por favor intenta de nuevo.');
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
                const feedback = input.parentNode.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.textContent = '';
                    feedback.style.display = 'none';
                }
            }
        });
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
window.CVForm = CVForm;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.cvForm = new CVForm();
});
