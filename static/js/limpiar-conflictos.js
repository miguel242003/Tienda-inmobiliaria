
// Archivo de limpieza para eliminar conflictos de ClickTracker
// Este archivo se puede eliminar después de usar

console.log('🧹 Iniciando limpieza de conflictos ClickTracker...');

// Limpiar variables globales conflictivas
if (window.ClickTracker) {
    delete window.ClickTracker;
    console.log('✅ ClickTracker eliminado');
}

if (window.TrackClicksInitialized) {
    delete window.TrackClicksInitialized;
    console.log('✅ TrackClicksInitialized eliminado');
}

if (window.PropertyClickTrackerInitialized) {
    delete window.PropertyClickTrackerInitialized;
    console.log('✅ PropertyClickTrackerInitialized eliminado');
}

// Limpiar cualquier referencia a tracking-clics.js
const scripts = document.querySelectorAll('script[src*="tracking-clics"]');
scripts.forEach(script => {
    script.remove();
    console.log('✅ Script tracking-clics.js removido del DOM');
});

// Limpiar event listeners duplicados
document.removeEventListener('DOMContentLoaded', function() {});
console.log('✅ Event listeners limpiados');

console.log('✅ Limpieza completada');
console.log('📋 Instrucciones:');
console.log('  1. Recarga la página (Ctrl+F5)');
console.log('  2. Verifica que no hay errores en la consola');
console.log('  3. Haz clic en "Ver Detalle" para probar');
console.log('  4. Elimina este archivo después de usar');
