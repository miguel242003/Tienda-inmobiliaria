/**
 * Optimizador de Consola - Reduce logs innecesarios
 * Versión: 1.0 - Solo logs importantes
 */
(function() {
    'use strict';
    
    // Guardar console original
    const originalConsole = {
        log: console.log,
        warn: console.warn,
        error: console.error,
        info: console.info,
        debug: console.debug
    };
    
    // Función para determinar si un log es importante
    function esLogImportante(mensaje) {
        const mensajeStr = String(mensaje).toLowerCase();
        
        // Mantener solo logs importantes
        const patronesImportantes = [
            'error',
            'exception',
            'failed',
            'success',
            'warning',
            'critical',
            'fatal',
            'timeout',
            'network',
            'connection',
            'auth',
            'security',
            'validation',
            'form',
            'submit',
            'ajax',
            'fetch',
            'response',
            'status'
        ];
        
        return patronesImportantes.some(patron => mensajeStr.includes(patron));
    }
    
    // Override console.log para filtrar logs
    console.log = function(...args) {
        const mensaje = args.join(' ');
        if (esLogImportante(mensaje)) {
            originalConsole.log.apply(console, args);
        }
    };
    
    // Override console.info para filtrar logs
    console.info = function(...args) {
        const mensaje = args.join(' ');
        if (esLogImportante(mensaje)) {
            originalConsole.info.apply(console, args);
        }
    };
    
    // Override console.debug para filtrar logs
    console.debug = function(...args) {
        const mensaje = args.join(' ');
        if (esLogImportante(mensaje)) {
            originalConsole.debug.apply(console, args);
        }
    };
    
    // Mantener console.warn y console.error sin filtros
    console.warn = originalConsole.warn;
    console.error = originalConsole.error;
    
    // Función para restaurar console original (para debugging)
    window.restoreConsole = function() {
        console.log = originalConsole.log;
        console.info = originalConsole.info;
        console.debug = originalConsole.debug;
        console.warn = originalConsole.warn;
        console.error = originalConsole.error;
    };
    
    // Función para habilitar todos los logs temporalmente
    window.enableAllLogs = function() {
        console.log = originalConsole.log;
        console.info = originalConsole.info;
        console.debug = originalConsole.debug;
    };
    
    // Función para deshabilitar todos los logs
    window.disableAllLogs = function() {
        console.log = function() {};
        console.info = function() {};
        console.debug = function() {};
        console.warn = function() {};
        console.error = function() {};
    };
    
    // Log de inicialización
    console.log('🔧 Console Optimizer activado - Solo logs importantes');
})();
