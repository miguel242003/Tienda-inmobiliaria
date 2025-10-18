/**
 * Sistema de Tracking de Clics - VERSIÓN SIMPLE
 * Registra clics directamente sin endpoint AJAX
 */
(function() {
    'use strict';
    
    console.log('🚀 Inicializando ClickTracker Simple...');
    
    // Función para registrar clic directamente
    function registrarClickSimple(propiedadId, paginaOrigen = 'home') {
        console.log('🎯 Registrando clic simple para propiedad:', propiedadId);
        
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
        
        console.log('✅ Clic simple enviado');
    }
    
    // Función para obtener token CSRF
    function obtenerTokenCSRF() {
        // Buscar en input hidden
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) {
            console.log('✅ Token CSRF encontrado en input');
            return csrfToken;
        }
        
        // Buscar en cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith('csrftoken=')) {
                csrfToken = trimmed.split('=')[1];
                console.log('✅ Token CSRF encontrado en cookies');
                return csrfToken;
            }
        }
        
        console.warn('⚠️ No se encontró token CSRF');
        return '';
    }
    
    // Función para detectar clics
    function detectarClics() {
        console.log('🔍 Buscando enlaces con data-propiedad-id...');
        
        // Buscar todos los enlaces con data-propiedad-id
        const enlaces = document.querySelectorAll('a[data-propiedad-id]');
        console.log(`📊 Encontrados ${enlaces.length} enlaces con data-propiedad-id`);
        
        enlaces.forEach((enlace, index) => {
            const propiedadId = enlace.getAttribute('data-propiedad-id');
            const href = enlace.getAttribute('href');
            
            console.log(`✅ Enlace ${index + 1}: ID ${propiedadId} - ${href}`);
            
            // Agregar event listener
            enlace.addEventListener('click', function(e) {
                console.log('🎯 CLICK DETECTADO en propiedad:', propiedadId);
                
                // Determinar página de origen
                const paginaOrigen = window.location.pathname.includes('buscar') ? 'buscar' : 'home';
                
                // Registrar clic
                registrarClickSimple(propiedadId, paginaOrigen);
                
                // Continuar con la navegación normal
                // No prevenir el comportamiento por defecto
            });
        });
        
        // También buscar botones con data-propiedad-id
        const botones = document.querySelectorAll('button[data-propiedad-id], input[data-propiedad-id]');
        console.log(`📊 Encontrados ${botones.length} botones con data-propiedad-id`);
        
        botones.forEach((boton, index) => {
            const propiedadId = boton.getAttribute('data-propiedad-id');
            console.log(`✅ Botón ${index + 1}: ID ${propiedadId}`);
            
            boton.addEventListener('click', function(e) {
                console.log('🎯 CLICK DETECTADO en botón propiedad:', propiedadId);
                
                const paginaOrigen = window.location.pathname.includes('buscar') ? 'buscar' : 'home';
                registrarClickSimple(propiedadId, paginaOrigen);
            });
        });
    }
    
    // Función para inicializar
    function inicializar() {
        console.log('🚀 Inicializando ClickTracker Simple...');
        
        // Detectar clics
        detectarClics();
        
        // Observar cambios en el DOM (para contenido dinámico)
        const observer = new MutationObserver(function(mutations) {
            mutations.forEach(function(mutation) {
                if (mutation.type === 'childList') {
                    console.log('🔄 DOM actualizado, re-escaneando enlaces...');
                    detectarClics();
                }
            });
        });
        
        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('✅ ClickTracker Simple inicializado correctamente');
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }
    
    // Exponer funciones globalmente para debugging
    window.ClickTrackerSimple = {
        registrarClick: registrarClickSimple,
        detectarClics: detectarClics,
        version: '1.0'
    };
    
    console.log('✅ ClickTracker Simple v1.0 cargado correctamente');
})();
