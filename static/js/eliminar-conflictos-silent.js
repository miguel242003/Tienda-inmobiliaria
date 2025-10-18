/**
 * Limpieza de Conflictos - VERSIÓN SILENCIOSA
 * Limpia conflictos sin mostrar mensajes en consola
 */
(function() {
    'use strict';
    
    // 1. Limpiar variables globales conflictivas
    if (typeof window.ClickTracker !== 'undefined') {
        delete window.ClickTracker;
    }
    
    // 2. Limpiar event listeners duplicados
    const enlaces = document.querySelectorAll('a[data-propiedad-id]');
    enlaces.forEach(enlace => {
        // Clonar el elemento para eliminar todos los event listeners
        const nuevoEnlace = enlace.cloneNode(true);
        enlace.parentNode.replaceChild(nuevoEnlace, enlace);
    });
    
    // 3. Limpiar event listeners conflictivos
    const botones = document.querySelectorAll('button[data-propiedad-id], input[data-propiedad-id]');
    botones.forEach(boton => {
        const nuevoBoton = boton.cloneNode(true);
        boton.parentNode.replaceChild(nuevoBoton, boton);
    });
    
    // 4. El script silencioso se carga directamente en base.html
    // No se cargan scripts automáticamente para evitar conflictos
    
})();
