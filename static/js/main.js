// JavaScript para la tienda inmobiliaria con menú responsive

document.addEventListener('DOMContentLoaded', function() {
    console.log('Página cargada correctamente');
    
    // ===== MENÚ RESPONSIVE =====
    const mobileMenuBtn = document.getElementById('mobileMenuBtn');
    const mobileMenuPanel = document.getElementById('mobileMenuPanel');
    const mobileOverlay = document.getElementById('mobileOverlay');
    const closeMenuBtn = document.getElementById('closeMenuBtn');
    
    // Función para abrir el menú móvil
    function openMobileMenu() {
        mobileMenuPanel.style.right = '0';
        mobileOverlay.style.display = 'block';
        mobileOverlay.style.opacity = '1';
        mobileOverlay.style.visibility = 'visible';
        document.body.style.overflow = 'hidden';
        
        // Cambiar hamburguesa a X
        mobileMenuBtn.classList.add('active');
    }
    
    // Función para cerrar el menú móvil
    function closeMobileMenu() {
        mobileMenuPanel.style.right = '-300px';
        mobileOverlay.style.display = 'none';
        mobileOverlay.style.opacity = '0';
        mobileOverlay.style.visibility = 'hidden';
        document.body.style.overflow = '';
        
        // Cambiar X a hamburguesa
        mobileMenuBtn.classList.remove('active');
    }
    
    // Event listeners para el menú móvil
    if (mobileMenuBtn) {
        mobileMenuBtn.addEventListener('click', openMobileMenu);
    }
    
    if (closeMenuBtn) {
        closeMenuBtn.addEventListener('click', closeMobileMenu);
    }
    
    if (mobileOverlay) {
        mobileOverlay.addEventListener('click', closeMobileMenu);
    }
    
    // Cerrar menú al hacer clic en un enlace
    const mobileNavItems = document.querySelectorAll('.mobile-nav-item');
    mobileNavItems.forEach(item => {
        item.addEventListener('click', closeMobileMenu);
    });
    
    // ===== FIN DEL MENÚ RESPONSIVE =====
    
    // ===== CARRUSEL DE IMÁGENES HERO =====
    const carousel = document.getElementById('heroCarousel');
    if (carousel) {
        const carouselItems = carousel.querySelectorAll('.carousel-item');
        const indicators = carousel.querySelectorAll('.indicator');
        let currentSlide = 0;
        let carouselInterval;
        
        // Función para mostrar una slide específica
        function showSlide(index) {
            // Ocultar todas las slides
            carouselItems.forEach((item, i) => {
                item.classList.remove('active');
            });
            
            // Desactivar todos los indicadores
            indicators.forEach((indicator, i) => {
                indicator.classList.remove('active');
            });
            
            // Mostrar la slide actual
            if (carouselItems[index]) {
                carouselItems[index].classList.add('active');
            }
            
            // Activar el indicador actual
            if (indicators[index]) {
                indicators[index].classList.add('active');
            }
            
            currentSlide = index;
        }
        
        // Función para ir a la siguiente slide
        function nextSlide() {
            const nextIndex = (currentSlide + 1) % carouselItems.length;
            showSlide(nextIndex);
        }
        
        // Función para ir a la slide anterior
        function prevSlide() {
            const prevIndex = (currentSlide - 1 + carouselItems.length) % carouselItems.length;
            showSlide(prevIndex);
        }
        
        // Iniciar rotación automática
        function startCarousel() {
            carouselInterval = setInterval(nextSlide, 8000); // 8 segundos
        }
        
        // Detener rotación automática
        function stopCarousel() {
            if (carouselInterval) {
                clearInterval(carouselInterval);
            }
        }
        
        // Event listeners para los indicadores
        indicators.forEach((indicator, index) => {
            indicator.addEventListener('click', () => {
                showSlide(index);
                stopCarousel();
                startCarousel(); // Reiniciar el temporizador después del clic
            });
        });
        
        // Pausar en hover y reanudar al salir
        carousel.addEventListener('mouseenter', stopCarousel);
        carousel.addEventListener('mouseleave', startCarousel);
        
        // Controles de teclado (opcional)
        document.addEventListener('keydown', (e) => {
            if (e.key === 'ArrowLeft') {
                prevSlide();
                stopCarousel();
                startCarousel();
            } else if (e.key === 'ArrowRight') {
                nextSlide();
                stopCarousel();
                startCarousel();
            }
        });
        
        // Inicializar el carrusel
        showSlide(0);
        startCarousel();
        
        console.log('Carrusel de imágenes inicializado correctamente');
    }
    // ===== FIN DEL CARRUSEL HERO =====
    
    // ===== ANIMACIÓN DE CONTADORES DE ESTADÍSTICAS =====
    function animateCounter(element, target, duration = 2000) {
        let start = 0;
        const increment = target / (duration / 16); // 60 FPS
        
        function updateCounter() {
            start += increment;
            if (start < target) {
                element.textContent = Math.floor(start);
                requestAnimationFrame(updateCounter);
            } else {
                element.textContent = target;
            }
        }
        
        updateCounter();
    }
    
    // Función para observar cuando las estadísticas entran en el viewport
    function observeStats() {
        const statsSection = document.querySelector('.stats-section');
        if (!statsSection) return;
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    // Animar todos los contadores
                    const counters = document.querySelectorAll('.stat-number');
                    counters.forEach(counter => {
                        const target = parseInt(counter.getAttribute('data-target'));
                        if (target && !counter.classList.contains('animated')) {
                            counter.classList.add('animated');
                            animateCounter(counter, target);
                        }
                    });
                    
                    // Una vez que se animan, desconectar el observador
                    observer.disconnect();
                }
            });
        }, {
            threshold: 0.3, // Cuando el 30% de la sección sea visible
            rootMargin: '0px 0px -100px 0px'
        });
        
        observer.observe(statsSection);
    }
    
    // Inicializar la observación de estadísticas
    observeStats();
    
    // ===== FIN DE ANIMACIÓN DE CONTADORES =====
    
    // Inicializar tooltips de Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Efectos hover en tarjetas de propiedades
    const propertyCards = document.querySelectorAll('.property-card');
    propertyCards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // Desplazamiento suave para enlaces ancla
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });
    
    // ===== DETECCIÓN DE PÁGINA ACTIVA =====
    function setActiveNavItem() {
        const currentPath = window.location.pathname;
        const navItems = document.querySelectorAll('.nav-item');
        
        navItems.forEach(item => {
            // Remover clase active de todos los elementos
            item.classList.remove('active');
            
            // Obtener la URL del enlace
            const href = item.getAttribute('href');
            
            // Verificar si es la página actual
            if (href === currentPath) {
                item.classList.add('active');
            }
            
            // Caso especial para la página de inicio
            if (currentPath === '/' && href.includes('home')) {
                item.classList.add('active');
            }
            
            // Caso especial para propiedades
            if (currentPath.includes('/propiedades/') && href.includes('propiedades')) {
                item.classList.add('active');
            }
        });
        
        console.log('Navegación activa configurada para:', currentPath);
    }
    
    // Configurar navegación activa al cargar la página
    setActiveNavItem();
    // ===== FIN DE DETECCIÓN DE PÁGINA ACTIVA =====
});