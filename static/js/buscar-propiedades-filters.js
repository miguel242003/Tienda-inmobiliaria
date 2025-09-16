/**
 * BUSCAR PROPIEDADES FILTERS - FILTER MANAGEMENT
 * =============================================
 * Handles the search filters functionality for the buscar propiedades page
 */

class BuscarPropiedadesFilters {
    constructor() {
        this.form = null;
        this.inputs = {};
        this.isInitialized = false;
        this.validationRules = {};
        
        this.init();
    }

    /**
     * Initialize filters
     */
    init() {
        if (this.isInitialized) return;
        
        try {
            this.cacheElements();
            this.setupValidation();
            this.bindEvents();
            this.isInitialized = true;
            
            console.log('Buscar Propiedades Filters initialized successfully');
        } catch (error) {
            console.error('Error initializing filters:', error);
        }
    }

    /**
     * Cache DOM elements
     */
    cacheElements() {
        this.form = document.querySelector('form[method="get"]');
        
        if (this.form) {
            this.inputs = {
                query: this.form.querySelector('#q'),
                tipo: this.form.querySelector('#tipo'),
                operacion: this.form.querySelector('#operacion'),
                precioMin: this.form.querySelector('#precio_min'),
                precioMax: this.form.querySelector('#precio_max')
            };
        }
    }

    /**
     * Setup validation rules
     */
    setupValidation() {
        this.validationRules = {
            precioMin: {
                min: 0,
                message: 'El precio mínimo no puede ser negativo'
            },
            precioMax: {
                min: 0,
                message: 'El precio máximo no puede ser negativo'
            }
        };
    }

    /**
     * Bind events
     */
    bindEvents() {
        if (!this.form) return;

        // Input validation
        Object.keys(this.inputs).forEach(key => {
            const input = this.inputs[key];
            if (input) {
                input.addEventListener('input', (e) => this.validateInput(e, key));
                input.addEventListener('blur', (e) => this.validateInput(e, key));
            }
        });

        // Form submission
        this.form.addEventListener('submit', (e) => this.handleSubmit(e));

        // Clear form
        const clearBtn = this.form.querySelector('a[href*="buscar"]');
        if (clearBtn) {
            clearBtn.addEventListener('click', (e) => this.handleClear(e));
        }

        // Auto-submit on select change
        const selects = this.form.querySelectorAll('select');
        selects.forEach(select => {
            select.addEventListener('change', () => this.autoSubmit());
        });
    }

    /**
     * Validate input
     */
    validateInput(event, inputName) {
        const input = event.target;
        const value = parseFloat(input.value);
        
        // Clear previous validation
        this.clearValidation(input);

        // Validate based on rules
        if (this.validationRules[inputName]) {
            const rule = this.validationRules[inputName];
            
            if (input.value && value < rule.min) {
                this.showValidationError(input, rule.message);
                return false;
            }
        }

        // Validate price range
        if (inputName === 'precioMin' && this.inputs.precioMax) {
            const precioMin = parseFloat(input.value);
            const precioMax = parseFloat(this.inputs.precioMax.value);
            
            if (precioMin && precioMax && precioMin > precioMax) {
                this.showValidationError(input, 'El precio mínimo no puede ser mayor al máximo');
                return false;
            }
        }

        if (inputName === 'precioMax' && this.inputs.precioMin) {
            const precioMin = parseFloat(this.inputs.precioMin.value);
            const precioMax = parseFloat(input.value);
            
            if (precioMin && precioMax && precioMin > precioMax) {
                this.showValidationError(input, 'El precio máximo no puede ser menor al mínimo');
                return false;
            }
        }

        return true;
    }

    /**
     * Show validation error
     */
    showValidationError(input, message) {
        input.classList.add('is-invalid');
        
        // Remove existing error message
        const existingError = input.parentNode.querySelector('.invalid-feedback');
        if (existingError) {
            existingError.remove();
        }

        // Add new error message
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        input.parentNode.appendChild(errorDiv);
    }

    /**
     * Clear validation
     */
    clearValidation(input) {
        input.classList.remove('is-invalid');
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    /**
     * Handle form submission
     */
    handleSubmit(event) {
        // Validate all inputs
        let isValid = true;
        
        Object.keys(this.inputs).forEach(key => {
            if (this.inputs[key] && !this.validateInput({ target: this.inputs[key] }, key)) {
                isValid = false;
            }
        });

        if (!isValid) {
            event.preventDefault();
            this.showNotification('error', 'Por favor corrige los errores en el formulario');
            return;
        }

        // Add loading state
        this.setLoadingState(true);
    }

    /**
     * Handle clear form
     */
    handleClear(event) {
        event.preventDefault();
        
        // Clear all inputs
        Object.values(this.inputs).forEach(input => {
            if (input) {
                input.value = '';
                this.clearValidation(input);
            }
        });

        // Submit form to get all properties
        this.form.submit();
    }

    /**
     * Auto-submit form on select change
     */
    autoSubmit() {
        // Small delay to allow user to see the change
        setTimeout(() => {
            this.form.submit();
        }, 100);
    }

    /**
     * Set loading state
     */
    setLoadingState(loading) {
        const submitBtn = this.form.querySelector('button[type="submit"]');
        if (submitBtn) {
            if (loading) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Buscando...';
            } else {
                submitBtn.disabled = false;
                submitBtn.innerHTML = '<i class="fas fa-search"></i> Buscar';
            }
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
     * Reset form
     */
    resetForm() {
        Object.values(this.inputs).forEach(input => {
            if (input) {
                input.value = '';
                this.clearValidation(input);
            }
        });
    }

    /**
     * Show notification
     */
    showNotification(type, message) {
        // Use global notification system if available
        if (window.mostrarNotificacion) {
            window.mostrarNotificacion(type, 'Filtros', message);
        } else {
            alert(message);
        }
    }

    /**
     * Get filter state
     */
    getFilterState() {
        return {
            isInitialized: this.isInitialized,
            formData: this.getFormData(),
            hasActiveFilters: this.hasActiveFilters()
        };
    }

    /**
     * Check if form has active filters
     */
    hasActiveFilters() {
        const data = this.getFormData();
        return Object.values(data).some(value => value && value.trim() !== '');
    }

    /**
     * Destroy filters
     */
    destroy() {
        if (this.form) {
            this.form.removeEventListener('submit', this.handleSubmit);
            
            Object.values(this.inputs).forEach(input => {
                if (input) {
                    input.removeEventListener('input', this.validateInput);
                    input.removeEventListener('blur', this.validateInput);
                }
            });
        }
        
        this.isInitialized = false;
    }
}

// Export for use in other modules
window.BuscarPropiedadesFilters = BuscarPropiedadesFilters;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.buscarPropiedadesFilters = new BuscarPropiedadesFilters();
});
