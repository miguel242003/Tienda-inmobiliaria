/**
 * Script para tracking de clics en botones "Ver Detalle" de propiedades
 * Registra automáticamente los clics en la base de datos
 * Versión: 2.1 - Prevención de conflictos y caché
 * Timestamp: 2025-01-27
 */

// Evitar conflictos con nombres existentes
(function() {
    'use strict';
    
    // Verificar si ya se inicializó para evitar múltiples cargas
    if (window.TrackClicksInitialized) {
        console.log('⚠️ TrackClicks ya inicializado, evitando duplicación');
        return;
    }
    
    // Marcar como inicializado inmediatamente
    window.TrackClicksInitialized = true;
    console.log('🚀 Inicializando TrackClicks v2.1...');
    
    // Función mejorada para registrar clics
    function registrarClick(propiedadId) {
        console.log('Registrando click para propiedad:', propiedadId);
        
        // Obtener token CSRF de múltiples fuentes
        let csrfToken = null;
        
        // 1. Buscar en input hidden
        const csrfInput = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfInput) {
            csrfToken = csrfInput.value;
            console.log('✅ Token CSRF encontrado en input hidden');
        }
        
        // 2. Buscar en cookies
        if (!csrfToken) {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                const trimmed = cookie.trim();
                if (trimmed.startsWith('csrftoken=')) {
                    csrfToken = trimmed.split('=')[1];
                    console.log('✅ Token CSRF encontrado en cookies');
                    break;
                }
            }
        }
        
        // 3. Buscar en meta tag
        if (!csrfToken) {
            const metaTag = document.querySelector('meta[name="csrf-token"]');
            if (metaTag) {
                csrfToken = metaTag.getAttribute('content');
                console.log('✅ Token CSRF encontrado en meta tag');
            }
        }
        
        if (!csrfToken) {
            console.warn('⚠️ No se encontró token CSRF, intentando sin él');
        }
        
        // Preparar headers
        const headers = {
            'Content-Type': 'application/json'
        };
        
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
        
        fetch('/propiedades/registrar-click', {
            method: 'POST',
            headers: headers,
            body: JSON.stringify({
                propiedad_id: propiedadId,
                pagina_origen: window.location.pathname.includes('buscar') ? 'buscar' : 'home'
            })
        })
        .then(response => {
            console.log('Response status:', response.status);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log('✅ Click registrado exitosamente');
            } else {
                console.error('❌ Error al registrar click:', data.error);
            }
        })
        .catch(error => {
            console.error('❌ Error de red:', error);
        });
    }
    
    // Inicializar cuando el DOM esté listo
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🚀 Inicializando tracking de clics v2.0...');
        
        // Buscar todos los enlaces que van a detalle de propiedades
        const enlacesDetalle = document.querySelectorAll('a[href*="/propiedades/"]');
        console.log('📊 Encontrados', enlacesDetalle.length, 'enlaces de propiedades');
        
        enlacesDetalle.forEach((enlace, index) => {
            const propiedadId = enlace.getAttribute('data-propiedad-id');
            
            if (propiedadId) {
                console.log('✅ Enlace', index + 1, ':', 'ID', propiedadId, '-', enlace.href);
                enlace.addEventListener('click', function(e) {
                    console.log('🎯 CLICK DETECTADO en propiedad:', propiedadId);
                    registrarClick(propiedadId);
                });
            } else {
                console.log('⚠️ Enlace', index + 1, ':', 'Sin data-propiedad-id -', enlace.href);
            }
        });
        
        console.log('✅ Tracking de clics inicializado correctamente');
    });
})();
