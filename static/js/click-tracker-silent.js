/**
 * Sistema de Tracking de Clics - VERSIÓN SILENCIOSA
 * Registra clics sin mostrar mensajes en consola
 */
(function() {
    'use strict';
    
    // Función para registrar clic directamente
    function registrarClickSilent(propiedadId, paginaOrigen = 'home') {
        // Crear un elemento oculto para enviar el clic
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/propiedades/registrar-click/';
        form.style.display = 'none';
        
        // Agregar campos
        const propiedadField = document.createElement('input');
        propiedadField.type = 'hidden';
        propiedadField.name = 'propiedad_id';
        propiedadField.value = propiedadId;
        
        const paginaField = document.createElement('input');
        paginaField.type = 'hidden';
        paginaField.name = 'pagina_origen';
        paginaField.value = paginaOrigen;
        
        // Obtener token CSRF
        const csrfToken = obtenerTokenCSRF();
        const csrfField = document.createElement('input');
        csrfField.type = 'hidden';
        csrfField.name = 'csrfmiddlewaretoken';
        csrfField.value = csrfToken;
        
        form.appendChild(propiedadField);
        form.appendChild(paginaField);
        form.appendChild(csrfField);
        
        // Agregar al DOM y enviar
        document.body.appendChild(form);
        form.submit();
    }
    
    // Función para obtener token CSRF
    function obtenerTokenCSRF() {
        // Buscar en input hidden
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            return csrfToken;
        }
        
        // Buscar en cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith('csrftoken=')) {
                csrfToken = trimmed.split('=')[1];
                return csrfToken;
            }
        }
        
        return '';
    }
    
    // Función para detectar clics
    function detectarClics() {
        // Buscar todos los enlaces con data-propiedad-id
        const enlaces = document.querySelectorAll('a[data-propiedad-id]');
        
        enlaces.forEach((enlace) => {
            const propiedadId = enlace.getAttribute('data-propiedad-id');
            
            // Agregar event listener
            enlace.addEventListener('click', function(e) {
                // Determinar página de origen
                const paginaOrigen = window.location.pathname.includes('buscar') ? 'buscar' : 'home';
                
                // Registrar clic
                registrarClickSilent(propiedadId, paginaOrigen);
            });
        });
        
        // También buscar botones con data-propiedad-id
        const botones = document.querySelectorAll('button[data-propiedad-id], input[data-propiedad-id]');
        
        botones.forEach((boton) => {
            const propiedadId = boton.getAttribute('data-propiedad-id');
            
            boton.addEventListener('click', function(e) {
                const paginaOrigen = window.location.pathname.includes('buscar') ? 'buscar' : 'home';
                registrarClickSilent(propiedadId, paginaOrigen);
            });
        });
    }
    
    // Función para inicializar
    function inicializar() {
        // Detectar clics
        detectarClics();
        
        // Observar cambios en el DOM (para contenido dinámico)
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    detectarClics();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }
    
    // Exponer funciones globalmente para debugging
    window.ClickTrackerSilent = {
        registrarClick: registrarClickSilent,
        detectarClics: detectarClics,
        version: '1.0'
    };
})();
