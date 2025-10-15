//**
* Script para tracking de clics en botones "Ver Detalle" de propiedades
* Registra automáticamente los clics en la base de datos
*/

if (!window.ClickTrackerInitialized) {
   window.ClickTrackerInitialized = true;

   class ClickTracker {
       constructor() {
           this.init();
       }

       init() {
           console.log('🔍 ClickTracker inicializando...');
           
           // Detectar la página actual
           this.paginaOrigen = this.detectarPaginaOrigen();
           console.log('📍 Página origen detectada:', this.paginaOrigen);
           
           // Agregar event listeners a todos los botones "Ver Detalle"
           this.agregarEventListeners();
           console.log('✅ ClickTracker inicializado correctamente');
       }

       detectarPaginaOrigen() {
           const path = window.location.pathname;
           
           if (path === '/' || path.includes('home')) {
               return 'home';
           } else if (path.includes('buscar') || path.includes('propiedades')) {
               return 'buscar';
           } else if (path.includes('detalle')) {
               return 'detalle';
           } else {
               return 'otra';
           }
       }

       agregarEventListeners() {
           console.log('🔍 Buscando enlaces de propiedades...');
           
           // Buscar todos los enlaces que van a detalle de propiedades
           const enlacesDetalle = document.querySelectorAll('a[href*="/propiedades/"]');
           console.log(`📊 Encontrados ${enlacesDetalle.length} enlaces de propiedades`);
           
           enlacesDetalle.forEach((enlace, index) => {
               const href = enlace.getAttribute('href');
               let propiedadId = enlace.getAttribute('data-propiedad-id');
               
               if (!propiedadId) {
                   const elementoPadre = enlace.closest('[data-propiedad-id]');
                   if (elementoPadre) {
                       propiedadId = elementoPadre.getAttribute('data-propiedad-id');
                   }
               }
               
               if (propiedadId) {
                   console.log(`✅ Enlace ${index + 1}: ID ${propiedadId} - ${href}`);
                   enlace.addEventListener('click', (e) => {
                       console.log(`🖱️ Click detectado en propiedad ${propiedadId}`);
                       this.registrarClick(propiedadId);
                   });
               } else {
                   console.log(`⚠️ Enlace ${index + 1}: Sin data-propiedad-id - ${href}`);
               }
           });

           const botonesDetalle = document.querySelectorAll('.btn-ver-detalle, .ver-detalle');
           botonesDetalle.forEach(boton => {
               const propiedadId = boton.getAttribute('data-propiedad-id');
               if (propiedadId) {
                   boton.addEventListener('click', (e) => {
                       this.registrarClick(propiedadId);
                   });
               }
           });
       }

       async registrarClick(propiedadId) {
           console.log('Iniciando registro de click para propiedad:', propiedadId);
           console.log('Página origen:', this.paginaOrigen);
           
           const csrfToken = this.getCSRFToken();
           console.log('CSRF Token:', csrfToken ? 'Encontrado' : 'No encontrado');
           
           try {
               const requestData = {
                   propiedad_id: propiedadId,
                   pagina_origen: this.paginaOrigen
               };
               
               console.log('Enviando datos:', requestData);
               
               const response = await fetch('/propiedades/registrar-click/', {
                   method: 'POST',
                   headers: {
                       'Content-Type': 'application/json',
                       'X-CSRFToken': csrfToken
                   },
                   body: JSON.stringify(requestData)
               });

               console.log('Response status:', response.status);
               const data = await response.json();
               
               if (data.success) {
                   console.log(`✅ Click registrado para propiedad ${propiedadId}`);
               } else {
                   console.error('❌ Error al registrar click:', data.error);
               }
           } catch (error) {
               console.error('❌ Error de red al registrar click:', error);
           }
       }

       getCSRFToken() {
