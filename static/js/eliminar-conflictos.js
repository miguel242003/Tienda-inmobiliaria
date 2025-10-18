/**
 * Script para eliminar TODOS los conflictos de tracking
 * Versión: 1.0 - Eliminación completa
 */
(function() {
    'use strict';
    
    console.log('🧹 Iniciando limpieza completa de conflictos...');
    
    // 1. Eliminar todas las variables globales conflictivas
    const variablesConflictivas = [
        'ClickTracker',
        'clickTracker', 
        'PropertyClickTracker',
        'propertyClickTracker',
        'trackingClics',
        'tracking_clics'
    ];
    
    variablesConflictivas.forEach(variable => {
        if (typeof window[variable] !== 'undefined') {
            console.log(`🧹 Eliminando variable global: ${variable}`);
            delete window[variable];
        }
    });
    
    // 2. Eliminar todos los scripts de tracking del DOM
    const scriptsConflictivos = document.querySelectorAll('script[src*="tracking"], script[src*="click-tracker"], script[src*="property-click"]');
    scriptsConflictivos.forEach(script => {
        console.log(`🧹 Eliminando script conflictivo: ${script.src}`);
        script.remove();
    });
    
    // 3. Limpiar event listeners conflictivos
    const enlaces = document.querySelectorAll('a[data-propiedad-id]');
    enlaces.forEach(enlace => {
        // Clonar el elemento para eliminar todos los event listeners
        const nuevoEnlace = enlace.cloneNode(true);
        enlace.parentNode.replaceChild(nuevoEnlace, enlace);
    });
    
    console.log('✅ Limpieza completa finalizada');
    
    // 4. Cargar el script funcional después de la limpieza (DESHABILITADO)
    // El script silencioso se carga directamente en base.html
    /*
    setTimeout(() => {
        console.log('🚀 Cargando script funcional...');
        const script = document.createElement('script');
        script.src = '/static/js/click-tracker-funcional.js?v=3.0';
        script.onload = () => console.log('✅ Script funcional cargado');
        script.onerror = () => console.error('❌ Error al cargar script funcional');
        document.head.appendChild(script);
    }, 100);
    */
    
})();
