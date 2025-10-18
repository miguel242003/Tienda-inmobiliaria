/**
 * Sistema de Tracking de Clics - VERSIÓN OPTIMIZADA
 * Versión: 5.0 - Logs mínimos, solo errores importantes
 */
(function() {
    'use strict';
    
    // Limpiar variables globales conflictivas
    if (typeof window.ClickTracker !== 'undefined') {
        delete window.ClickTracker;
    }
    
    // Función principal para registrar clics
    function registrarClick(propiedadId, paginaOrigen = 'home') {
        // Obtener token CSRF
        const csrfToken = obtenerTokenCSRF();
        
        // Preparar datos
        const datos = {
            propiedad_id: parseInt(propiedadId),
            pagina_origen: paginaOrigen
        };
        
        // Enviar petición AJAX
        fetch('/propiedades/registrar-click/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(datos)
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar notificación visual (opcional)
                mostrarNotificacion('Click registrado correctamente');
            } else {
                console.error('❌ Error al registrar click:', data.error);
                mostrarNotificacion('Error al registrar click', 'error');
            }
        })
        .catch(error => {
            console.error('❌ Error de red:', error);
            mostrarNotificacion('Error de conexión', 'error');
        });
    }
    
    // Función para obtener token CSRF
    function obtenerTokenCSRF() {
        // Buscar en input hidden
        let csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (csrfToken) return csrfToken;
        
        // Buscar en cookies
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const trimmed = cookie.trim();
            if (trimmed.startsWith('csrftoken=')) {
                return trimmed.split('=')[1];
            }
        }
        
        // Buscar en meta tag
        const metaTag = document.querySelector('meta[name="csrf-token"]');
        if (metaTag) {
            return metaTag.getAttribute('content');
        }
        
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
        // Buscar todos los enlaces con data-propiedad-id
        const enlaces = document.querySelectorAll('a[data-propiedad-id]');
        
        enlaces.forEach((enlace) => {
            const propiedadId = enlace.getAttribute('data-propiedad-id');
            
            // Agregar event listener
            enlace.addEventListener('click', function(e) {
                // Determinar página de origen
                const paginaOrigen = window.location.pathname.includes('buscar') ? 'buscar' : 'home';
                
                // Registrar clic
                registrarClick(propiedadId, paginaOrigen);
            });
        });
        
        // También buscar botones con data-propiedad-id
        const botones = document.querySelectorAll('button[data-propiedad-id], input[data-propiedad-id]');
        
        botones.forEach((boton) => {
            const propiedadId = boton.getAttribute('data-propiedad-id');
            
            boton.addEventListener('click', function(e) {
                const paginaOrigen = window.location.pathname.includes('buscar') ? 'buscar' : 'home';
                registrarClick(propiedadId, paginaOrigen);
            });
        });
    }
    
    // Función para inicializar el tracker
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
    window.ClickTracker = {
        registrarClick: registrarClick,
        detectarClics: detectarClics,
        version: '5.0'
    };
})();
