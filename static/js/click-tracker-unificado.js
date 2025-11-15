/**
 * Sistema de Tracking de Clics - VERSIÓN UNIFICADA Y FUNCIONAL
 * Versión: 4.0 - Sin conflictos, completamente funcional
 */
(function() {
    'use strict';
    
    console.log('🚀 Inicializando ClickTracker Unificado v4.0...');
    
    // Limpiar variables globales conflictivas
    if (typeof window.ClickTracker !== 'undefined') {
        console.log('🧹 Limpiando ClickTracker anterior...');
        delete window.ClickTracker;
    }
    
    // Función principal para registrar clics
    function registrarClick(propiedadId, paginaOrigen = 'home') {
        console.log('🎯 Registrando clic para propiedad:', propiedadId);
        
        // Obtener token CSRF
        const csrfToken = obtenerTokenCSRF();
        
        // Preparar datos
        const datos = {
            propiedad_id: parseInt(propiedadId),
            pagina_origen: paginaOrigen
        };
        
        console.log('📤 Enviando datos:', datos);
        
        // Enviar petición AJAX
        fetch('/propiedades/registrar-click/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(datos)
        })
        .then(response => {
            console.log('📡 Respuesta del servidor:', response.status);
            return response.json();
        })
        .then(data => {
            if (data.success) {
                console.log('✅ Click registrado exitosamente');
                console.log('📊 Total clics:', data.total_clicks || 'N/A');
                
                // Mostrar notificación visual (opcional)
                mostrarNotificacion('Click registrado correctamente');
            } else {
                console.error('❌ Error al registrar click:', data.error);
                mostrarNotificacion('Error al registrar click', 'error');
            }
        })
        .catch(error => {
            // No mostrar error si la petición fue cancelada por navegación
            if (error.name === 'AbortError' || error.message === 'Failed to fetch' || 
                document.visibilityState === 'hidden' || document.hidden) {
                // La petición fue cancelada, no mostrar error
                return;
            }
            console.error('❌ Error de red:', error);
            // Solo mostrar error si la página sigue visible
            if (!document.hidden) {
                mostrarNotificacion('Error de conexión', 'error');
            }
        });
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
        
        // Buscar en meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            csrfToken = metaTag.getAttribute('content');
            console.log('✅ Token CSRF encontrado en meta tag');
            return csrfToken;
        }
        
        console.warn('⚠️ No se encontró token CSRF');
        return '';
    }
    
    // Función para mostrar notificaciones
    function mostrarNotificacion(mensaje, tipo = 'success') {
        // Crear elemento de notificación
        const notificacion = document.createElement('div');
        notificacion.className = `alert alert-${tipo === 'error' ? 'danger' : 'success'} alert-dismissible fade show`;
        notificacion.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            min-width: 300px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        `;
        notificacion.innerHTML = `
            <strong>${tipo === 'error' ? '❌' : '✅'}</strong> ${mensaje}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Agregar al DOM
        document.body.appendChild(notificacion);
        
        // Auto-remover después de 3 segundos
        setTimeout(() => {
            if (notificacion.parentNode) {
                notificacion.parentNode.removeChild(notificacion);
            }
        }, 3000);
    }
    
    // Función para detectar clics en enlaces
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
                registrarClick(propiedadId, paginaOrigen);
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
                registrarClick(propiedadId, paginaOrigen);
            });
        });
    }
    
    // Función para inicializar el tracker
    function inicializar() {
        console.log('🚀 Inicializando ClickTracker Unificado...');
        
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
        
        console.log('✅ ClickTracker Unificado inicializado correctamente');
    }
    
    // Inicializar cuando el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', inicializar);
    } else {
        inicializar();
    }
    
    // Exponer funciones globalmente para debugging
    window.ClickTracker = {
        registrarClick: registrarClick,
        detectarClics: detectarClics,
        version: '4.0'
    };
    
    console.log('✅ ClickTracker Unificado v4.0 cargado correctamente');
})();
