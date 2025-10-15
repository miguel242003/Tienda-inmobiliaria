// Archivo de limpieza para eliminar conflictos de tracking
// Este archivo se puede eliminar después de usar

console.log('🧹 Iniciando limpieza de conflictos...');

// Limpiar variables globales conflictivas
if (window.ClickTracker) {
    delete window.ClickTracker;
    console.log('🧹 ClickTracker eliminado');
}

if (window.TrackClicksInitialized) {
    delete window.TrackClicksInitialized;
    console.log('🧹 TrackClicksInitialized eliminado');
}

// Limpiar event listeners duplicados
document.removeEventListener('DOMContentLoaded', function() {});
console.log('🧹 Event listeners limpiados');

// Forzar recarga del script correcto
if (!window.PropertyClickTrackerInitialized) {
    console.log('🔄 Forzando recarga del script correcto...');
    // El script correcto se cargará automáticamente
}

console.log('✅ Limpieza completada');