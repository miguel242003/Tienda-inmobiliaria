/**
 * Script para tracking de clics en botones "Ver Detalle" de propiedades
 * Registra automáticamente los clics en la base de datos
 */

// Verificar si ya se inicializó para evitar múltiples cargas
if (window.ClickTrackerInitialized) {
    console.log('ClickTracker ya inicializado, saltando...');
} else {
    window.ClickTrackerInitialized = true;
    
    // Usar función en lugar de clase para evitar conflictos
    window.ClickTracker = function() {
        this.init();
    }

    window.ClickTracker.prototype.init = function() {
        // Detectar la página actual
        this.paginaOrigen = this.detectarPaginaOrigen();
        
        // Agregar event listeners a todos los botones "Ver Detalle"
        this.agregarEventListeners();
    }

    window.ClickTracker.prototype.detectarPaginaOrigen = function() {
        const path = window.location.pathname;
        
        if (path === '/' || path.includes('home')) {
            return 'home';
        } else if (path.includes('buscar') || path.includes('propiedades')) {
            return 'buscar';
        } else if (path.includes('detalle')) {
            return 'detalle';
        } else {
            return 'otra';
        }
    }

    window.ClickTracker.prototype.agregarEventListeners = function() {
        console.log('=== INICIANDO AGREGAR EVENT LISTENERS ===');
        // Buscar todos los enlaces que van a detalle de propiedades
        const enlacesDetalle = document.querySelectorAll('a[href*="/propiedades/"]');
        console.log('Enlaces encontrados:', enlacesDetalle.length);
        
        enlacesDetalle.forEach(enlace => {
            const href = enlace.getAttribute('href');
            
            // Buscar data-propiedad-id en el enlace o en elementos padre
            let propiedadId = enlace.getAttribute('data-propiedad-id');
            
            if (!propiedadId) {
                // Buscar en el elemento padre más cercano que tenga data-propiedad-id
                const elementoPadre = enlace.closest('[data-propiedad-id]');
                if (elementoPadre) {
                    propiedadId = elementoPadre.getAttribute('data-propiedad-id');
                }
            }
            
            if (propiedadId) {
                console.log('Agregando listener para propiedad:', propiedadId);
                // Agregar event listener para el click
                enlace.addEventListener('click', (e) => {
                    console.log('CLICK DETECTADO en propiedad:', propiedadId);
                    this.registrarClick(propiedadId);
                });
            } else {
                console.log('No se encontró data-propiedad-id para enlace:', href);
            }
        });

        // También buscar botones con clase específica
        const botonesDetalle = document.querySelectorAll('.btn-ver-detalle, .ver-detalle');
        botonesDetalle.forEach(boton => {
            const propiedadId = boton.getAttribute('data-propiedad-id');
            if (propiedadId) {
                boton.addEventListener('click', (e) => {
                    this.registrarClick(propiedadId);
                });
            }
        });
    }

    window.ClickTracker.prototype.registrarClick = async function(propiedadId) {
        console.log('Iniciando registro de click para propiedad:', propiedadId);
        console.log('Página origen:', this.paginaOrigen);
        
        const csrfToken = this.getCSRFToken();
        console.log('CSRF Token:', csrfToken ? 'Encontrado' : 'No encontrado');
        
        try {
            const requestData = {
                propiedad_id: propiedadId,
                pagina_origen: this.paginaOrigen
            };
            
            console.log('Enviando datos:', requestData);
            
            const response = await fetch('/propiedades/registrar-click/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify(requestData)
            });

            console.log('Response status:', response.status);
            console.log('Response headers:', response.headers);
            
            const data = await response.json();
            console.log('Response data:', data);
            
            if (data.success) {
                console.log(`✅ Click registrado para propiedad ${propiedadId}`);
            } else {
                console.error('❌ Error al registrar click:', data.error);
            }
        } catch (error) {
            console.error('❌ Error de red al registrar click:', error);
        }
    }

    window.ClickTracker.prototype.getCSRFToken = function() {
        // Buscar el token CSRF en las cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                console.log('CSRF token encontrado en cookies:', value);
                return value;
            }
        }
        
        // Si no está en cookies, buscar en el DOM
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            console.log('CSRF token encontrado en DOM:', csrfToken.value);
            return csrfToken.value;
        }
        
        // Buscar en meta tags
        const metaToken = document.querySelector('meta[name=csrf-token]');
        if (metaToken) {
            console.log('CSRF token encontrado en meta:', metaToken.content);
            return metaToken.content;
        }
        
        console.warn('No se encontró token CSRF');
        return '';
    }
}

    }

    // Inicializar el tracker cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        new window.ClickTracker();
    });
}
