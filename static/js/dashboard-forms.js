/**
 * DASHBOARD FORMS - FORM MANAGEMENT
 * ================================
 * Handles all form-related functionality
 */

class DashboardForms {
    constructor() {
        this.forms = new Map();
        this.uploadAreas = new Map();
        this.isInitialized = false;
        
        this.init();
    }

    /**
     * Initialize forms
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.setupFormValidation();
            this.setupFileUploads();
            this.setupFormSubmissions();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('Dashboard Forms initialized successfully');
        } catch (error) {
            console.error('Error initializing forms:', error);
        }
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('form[data-validate]');
        forms.forEach(form => {
            this.setupFormValidation(form);
        });
    }

    /**
     * Setup individual form validation
     */
    setupFormValidation(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
            input.addEventListener('blur', () => this.validateField(input));
            input.addEventListener('input', () => this.clearFieldError(input));
        });
    }

    /**
     * Validate individual field
     */
    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.hasAttribute('required');
        
        let isValid = true;
        let errorMessage = '';

        // Required validation
        if (required && !value) {
            isValid = false;
            errorMessage = 'Este campo es obligatorio';
        }

        // Email validation
        if (type === 'email' && value) {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) {
                isValid = false;
                errorMessage = 'Ingresa un email válido';
            }
        }

        // Phone validation
        if (type === 'tel' && value) {
            const phoneRegex = /^[\+]?[1-9][\d]{0,15}$/;
            if (!phoneRegex.test(value.replace(/\s/g, ''))) {
                isValid = false;
                errorMessage = 'Ingresa un teléfono válido';
            }
        }

        // Number validation
        if (type === 'number' && value) {
            const num = parseFloat(value);
            const min = parseFloat(field.getAttribute('min'));
            const max = parseFloat(field.getAttribute('max'));
            
            if (isNaN(num)) {
                isValid = false;
                errorMessage = 'Ingresa un número válido';
            } else if (min !== null && num < min) {
                isValid = false;
                errorMessage = `El valor mínimo es ${min}`;
            } else if (max !== null && num > max) {
                isValid = false;
                errorMessage = `El valor máximo es ${max}`;
            }
        }

        // Update field state
        this.updateFieldState(field, isValid, errorMessage);
        
        return isValid;
    }

    /**
     * Update field visual state
     */
    updateFieldState(field, isValid, errorMessage) {
        const fieldContainer = field.closest('.form-group') || field.parentElement;
        
        // Remove existing error state
        fieldContainer.classList.remove('error');
        const existingError = fieldContainer.querySelector('.field-error');
        if (existingError) {
            existingError.remove();
        }

        if (!isValid) {
            // Add error state
            fieldContainer.classList.add('error');
            field.classList.add('border-red-500');
            
            // Add error message
            const errorElement = document.createElement('div');
            errorElement.className = 'field-error text-red-500 text-sm mt-1';
            errorElement.textContent = errorMessage;
            fieldContainer.appendChild(errorElement);
        } else {
            // Remove error state
            field.classList.remove('border-red-500');
            field.classList.add('border-green-500');
        }
    }

    /**
     * Clear field error
     */
    clearFieldError(field) {
        const fieldContainer = field.closest('.form-group') || field.parentElement;
        fieldContainer.classList.remove('error');
        field.classList.remove('border-red-500', 'border-green-500');
        
        const errorElement = fieldContainer.querySelector('.field-error');
        if (errorElement) {
            errorElement.remove();
        }
    }

    /**
     * Setup file uploads
     */
    setupFileUploads() {
        const uploadAreas = document.querySelectorAll('.upload-area');
        uploadAreas.forEach(area => {
            this.setupUploadArea(area);
        });
    }

    /**
     * Setup individual upload area
     */
    setupUploadArea(area) {
        const input = area.querySelector('input[type="file"]');
        if (!input) return;

        // Drag and drop events
        area.addEventListener('dragover', (e) => {
            e.preventDefault();
            area.classList.add('dragover');
        });

        area.addEventListener('dragleave', () => {
            area.classList.remove('dragover');
        });

        area.addEventListener('drop', (e) => {
            e.preventDefault();
            area.classList.remove('dragover');
            
            const files = e.dataTransfer.files;
            this.handleFiles(files, input);
        });

        // Click to upload
        area.addEventListener('click', () => {
            input.click();
        });

        // File input change
        input.addEventListener('change', (e) => {
            this.handleFiles(e.target.files, input);
        });
    }

    /**
     * Handle uploaded files
     */
    handleFiles(files, input) {
        if (!files.length) return;

        const allowedTypes = input.getAttribute('accept')?.split(',').map(type => type.trim()) || [];
        const maxSize = parseInt(input.getAttribute('data-max-size')) || 5 * 1024 * 1024; // 5MB default

        Array.from(files).forEach(file => {
            // Validate file type
            if (allowedTypes.length && !allowedTypes.some(type => {
                if (type.startsWith('.')) {
                    return file.name.toLowerCase().endsWith(type.toLowerCase());
                }
                return file.type.includes(type.replace('*', ''));
            })) {
                this.showError(`Tipo de archivo no permitido: ${file.name}`);
                return;
            }

            // Validate file size
            if (file.size > maxSize) {
                this.showError(`Archivo demasiado grande: ${file.name}`);
                return;
            }

            // Process file
            this.processFile(file, input);
        });
    }

    /**
     * Process individual file
     */
    processFile(file, input) {
        const previewContainer = input.closest('.upload-area').querySelector('.upload-preview');
        
        if (file.type.startsWith('image/')) {
            this.createImagePreview(file, previewContainer);
        } else {
            this.createFilePreview(file, previewContainer);
        }
    }

    /**
     * Create image preview
     */
    createImagePreview(file, container) {
        const reader = new FileReader();
        reader.onload = (e) => {
            const preview = document.createElement('div');
            preview.className = 'upload-preview-item';
            preview.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <div class="upload-preview-info">
                    <small>${file.name}</small>
                </div>
                <button type="button" class="upload-preview-remove" onclick="this.parentElement.remove()">
                    <i class="fas fa-times"></i>
                </button>
            `;
            container.appendChild(preview);
        };
        reader.readAsDataURL(file);
    }

    /**
     * Create file preview
     */
    createFilePreview(file, container) {
        const preview = document.createElement('div');
        preview.className = 'upload-preview-item';
        preview.innerHTML = `
            <div class="upload-preview-info">
                <i class="fas fa-file"></i>
                <small>${file.name}</small>
                <small>(${this.formatFileSize(file.size)})</small>
            </div>
            <button type="button" class="upload-preview-remove" onclick="this.parentElement.remove()">
                <i class="fas fa-times"></i>
            </button>
        `;
        container.appendChild(preview);
    }

    /**
     * Format file size
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Setup form submissions
     */
    setupFormSubmissions() {
        const forms = document.querySelectorAll('form[data-ajax]');
        forms.forEach(form => {
            form.addEventListener('submit', (e) => this.handleFormSubmit(e));
        });
    }

    /**
     * Handle form submission
     */
    async handleFormSubmit(event) {
        event.preventDefault();
        
        const form = event.target;
        const submitBtn = form.querySelector('button[type="submit"]');
        const originalText = submitBtn.textContent;
        
        try {
            // Validate form
            const isValid = this.validateForm(form);
            if (!isValid) {
                this.showError('Por favor corrige los errores en el formulario');
                return;
            }

            // Show loading state
            this.showLoading(submitBtn, 'Enviando...');

            // Prepare form data
            const formData = new FormData(form);
            
            // Submit form
            const response = await fetch(form.action, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            const result = await response.json();

            if (result.success) {
                this.showSuccess(result.message || 'Formulario enviado exitosamente');
                form.reset();
                this.clearAllErrors(form);
            } else {
                this.showError(result.message || 'Error al enviar el formulario');
                if (result.errors) {
                    this.showFieldErrors(form, result.errors);
                }
            }

        } catch (error) {
            console.error('Error submitting form:', error);
            this.showError('Error de conexión. Por favor intenta de nuevo.');
        } finally {
            this.hideLoading(submitBtn, originalText);
        }
    }

    /**
     * Validate entire form
     */
    validateForm(form) {
        const inputs = form.querySelectorAll('input, textarea, select');
        let isValid = true;

        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });

        return isValid;
    }

    /**
     * Show field errors
     */
    showFieldErrors(form, errors) {
        Object.keys(errors).forEach(fieldName => {
            const field = form.querySelector(`[name="${fieldName}"]`);
            if (field) {
                this.updateFieldState(field, false, errors[fieldName][0]);
            }
        });
    }

    /**
     * Clear all form errors
     */
    clearAllErrors(form) {
        const errorElements = form.querySelectorAll('.field-error');
        errorElements.forEach(element => element.remove());
        
        const errorFields = form.querySelectorAll('.error');
        errorFields.forEach(field => field.classList.remove('error'));
        
        const inputs = form.querySelectorAll('input, textarea, select');
        inputs.forEach(input => {
            input.classList.remove('border-red-500', 'border-green-500');
        });
    }

    /**
     * Show loading state
     */
    showLoading(button, text) {
        button.disabled = true;
        button.innerHTML = `<i class="fas fa-spinner fa-spin mr-2"></i>${text}`;
    }

    /**
     * Hide loading state
     */
    hideLoading(button, originalText) {
        button.disabled = false;
        button.innerHTML = originalText;
    }

    /**
     * Show success message
     */
    showSuccess(message) {
        if (window.mostrarNotificacion) {
            window.mostrarNotificacion('success', 'Éxito', message);
        } else {
            alert(message);
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        if (window.mostrarNotificacion) {
            window.mostrarNotificacion('error', 'Error', message);
        } else {
            alert(message);
        }
    }

    /**
     * Bind events
     */
    bindEvents() {
        // Global form events
        document.addEventListener('change', (e) => {
            if (e.target.matches('input[type="checkbox"]')) {
                this.handleCheckboxChange(e.target);
            }
        });
    }

    /**
     * Handle checkbox changes
     */
    handleCheckboxChange(checkbox) {
        const label = checkbox.nextElementSibling;
        if (label && label.tagName === 'LABEL') {
            if (checkbox.checked) {
                label.classList.add('text-primary-600', 'font-semibold');
            } else {
                label.classList.remove('text-primary-600', 'font-semibold');
            }
        }
    }

    /**
     * Destroy forms
     */
    destroy() {
        this.forms.clear();
        this.uploadAreas.clear();
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.DashboardForms = DashboardForms;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardForms = new DashboardForms();
});
