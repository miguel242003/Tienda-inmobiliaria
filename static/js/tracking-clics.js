/**
 * Script para tracking de clics en botones "Ver Detalle" de propiedades
 * Registra automáticamente los clics en la base de datos
 */

// Verificar si ya se inicializó para evitar múltiples cargas
if (window.ClickTrackerInitialized) {
    return;
}

window.ClickTrackerInitialized = true;

// Función simple para registrar clics
function registrarClick(propiedadId) {
    console.log('Registrando click para propiedad:', propiedadId);
    
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='))?.split('=')[1];
    
    fetch('/propiedades/registrar-click/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify({
            propiedad_id: propiedadId,
            pagina_origen: window.location.pathname.includes('buscar') ? 'buscar' : 'home'
        })
    })
    .then(response => response.json())
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
    // Buscar todos los enlaces que van a detalle de propiedades
    const enlacesDetalle = document.querySelectorAll('a[href*="/propiedades/"]');
    
    enlacesDetalle.forEach(enlace => {
        const propiedadId = enlace.getAttribute('data-propiedad-id');
        
        if (propiedadId) {
            enlace.addEventListener('click', function(e) {
                registrarClick(propiedadId);
            });
        }
    });
});