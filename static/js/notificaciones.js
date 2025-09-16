/**
 * Sistema de Notificaciones Hermosas
 * Sistema reutilizable para mostrar notificaciones elegantes en toda la aplicación
 */

// Función para mostrar notificaciones hermosas
function mostrarNotificacion(tipo, titulo, mensaje, duracion = 4000) {
    // Crear el contenedor de notificaciones si no existe
    let container = document.getElementById('notificaciones-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'notificaciones-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 10000;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }
    
    // Definir colores y iconos según el tipo
    const configs = {
        success: {
            color: '#4CAF50',
            icon: 'fas fa-check-circle',
            bgColor: 'linear-gradient(135deg, #4CAF50, #45a049)',
            borderColor: '#4CAF50'
        },
        error: {
            color: '#f44336',
            icon: 'fas fa-exclamation-circle',
            bgColor: 'linear-gradient(135deg, #f44336, #d32f2f)',
            borderColor: '#f44336'
        },
        warning: {
            color: '#ff9800',
            icon: 'fas fa-exclamation-triangle',
            bgColor: 'linear-gradient(135deg, #ff9800, #f57c00)',
            borderColor: '#ff9800'
        },
        info: {
            color: '#2196F3',
            icon: 'fas fa-info-circle',
            bgColor: 'linear-gradient(135deg, #2196F3, #1976D2)',
            borderColor: '#2196F3'
        }
    };
    
    const config = configs[tipo] || configs.info;
    
    // Crear la notificación
    const notificacion = document.createElement('div');
    notificacion.style.cssText = `
        background: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        border-left: 4px solid ${config.borderColor};
        max-width: 400px;
        min-width: 300px;
        position: relative;
        animation: slideInRight 0.4s ease;
        cursor: pointer;
        transition: all 0.3s ease;
    `;
    
    notificacion.innerHTML = `
        <div style="display: flex; align-items: flex-start; gap: 15px;">
            <div style="
                width: 40px;
                height: 40px;
                background: ${config.bgColor};
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                flex-shrink: 0;
                animation: pulse 0.6s ease;
            ">
                <i class="${config.icon}" style="color: white; font-size: 18px;"></i>
            </div>
            
            <div style="flex: 1;">
                <h4 style="
                    margin: 0 0 8px 0;
                    color: #2c3e50;
                    font-size: 16px;
                    font-weight: 600;
                ">${titulo}</h4>
                
                <p style="
                    margin: 0;
                    color: #7f8c8d;
                    font-size: 14px;
                    line-height: 1.4;
                ">${mensaje}</p>
            </div>
            
            <button onclick="cerrarNotificacion(this)" style="
                background: none;
                border: none;
                color: #bdc3c7;
                font-size: 18px;
                cursor: pointer;
                padding: 0;
                width: 24px;
                height: 24px;
                display: flex;
                align-items: center;
                justify-content: center;
                border-radius: 50%;
                transition: all 0.2s ease;
            " onmouseover="this.style.background='#ecf0f1'; this.style.color='#e74c3c'" 
               onmouseout="this.style.background='none'; this.style.color='#bdc3c7'">
                <i class="fas fa-times"></i>
            </button>
        </div>
        
        <div style="
            position: absolute;
            bottom: 0;
            left: 0;
            height: 3px;
            background: ${config.bgColor};
            border-radius: 0 0 12px 12px;
            animation: progressBar ${duracion}ms linear;
        "></div>
    `;
    
    // Agregar estilos CSS si no existen
    if (!document.getElementById('notificaciones-styles')) {
        const styles = document.createElement('style');
        styles.id = 'notificaciones-styles';
        styles.textContent = `
            @keyframes slideInRight {
                from {
                    opacity: 0;
                    transform: translateX(100%);
                }
                to {
                    opacity: 1;
                    transform: translateX(0);
                }
            }
            
            @keyframes slideOutRight {
                from {
                    opacity: 1;
                    transform: translateX(0);
                }
                to {
                    opacity: 0;
                    transform: translateX(100%);
                }
            }
            
            @keyframes pulse {
                0% { transform: scale(1); }
                50% { transform: scale(1.1); }
                100% { transform: scale(1); }
            }
            
            @keyframes progressBar {
                from { width: 100%; }
                to { width: 0%; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    // Agregar efecto hover
    notificacion.addEventListener('mouseenter', () => {
        notificacion.style.transform = 'translateX(-5px)';
        notificacion.style.boxShadow = '0 15px 40px rgba(0, 0, 0, 0.25)';
    });
    
    notificacion.addEventListener('mouseleave', () => {
        notificacion.style.transform = 'translateX(0)';
        notificacion.style.boxShadow = '0 10px 30px rgba(0, 0, 0, 0.2)';
    });
    
    // Agregar a la página
    container.appendChild(notificacion);
    
    // Auto-eliminar después del tiempo especificado
    setTimeout(() => {
        if (notificacion.parentNode) {
            cerrarNotificacion(notificacion.querySelector('button'));
        }
    }, duracion);
}

// Función para cerrar notificaciones
function cerrarNotificacion(button) {
    const notificacion = button.closest('div');
    notificacion.style.animation = 'slideOutRight 0.3s ease';
    setTimeout(() => {
        if (notificacion.parentNode) {
            notificacion.remove();
        }
    }, 300);
}

// Función para mostrar mensaje de éxito personalizado (para reseñas)
function mostrarMensajeExitoResena() {
    // Crear el modal de éxito
    const successModal = document.createElement('div');
    successModal.id = 'modal-exito-resena';
    successModal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 10000;
        animation: fadeIn 0.3s ease;
    `;
    
    successModal.innerHTML = `
        <div style="
            background: white;
            border-radius: 20px;
            padding: 40px;
            text-align: center;
            max-width: 500px;
            width: 90%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            animation: slideIn 0.4s ease;
            position: relative;
        ">
            <div style="
                width: 80px;
                height: 80px;
                background: linear-gradient(135deg, #4CAF50, #45a049);
                border-radius: 50%;
                margin: 0 auto 20px;
                display: flex;
                align-items: center;
                justify-content: center;
                animation: bounce 0.6s ease;
            ">
                <i class="fas fa-check" style="color: white; font-size: 32px;"></i>
            </div>
            
            <h3 style="
                color: #2c3e50;
                margin-bottom: 15px;
                font-size: 24px;
                font-weight: 600;
            ">¡Reseña Enviada!</h3>
            
            <p style="
                color: #7f8c8d;
                font-size: 16px;
                line-height: 1.5;
                margin-bottom: 25px;
            ">Tu reseña ha sido enviada exitosamente y será revisada antes de publicarse.</p>
            
            <div style="
                background: #f8f9fa;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 25px;
                border-left: 4px solid #4CAF50;
            ">
                <p style="
                    color: #495057;
                    font-size: 14px;
                    margin: 0;
                    font-style: italic;
                ">📝 Nuestro equipo revisará tu reseña en las próximas 24 horas</p>
            </div>
            
            <button onclick="cerrarMensajeExitoResena()" style="
                background: linear-gradient(135deg, #4CAF50, #45a049);
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 25px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
            " onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 6px 20px rgba(76, 175, 80, 0.4)'" 
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 15px rgba(76, 175, 80, 0.3)'">
                <i class="fas fa-thumbs-up" style="margin-right: 8px;"></i>
                ¡Entendido!
            </button>
        </div>
    `;
    
    // Agregar estilos CSS para las animaciones
    if (!document.getElementById('success-modal-styles')) {
        const styles = document.createElement('style');
        styles.id = 'success-modal-styles';
        styles.textContent = `
            @keyframes fadeIn {
                from { opacity: 0; }
                to { opacity: 1; }
            }
            
            @keyframes slideIn {
                from { 
                    opacity: 0;
                    transform: translateY(-50px) scale(0.9);
                }
                to { 
                    opacity: 1;
                    transform: translateY(0) scale(1);
                }
            }
            
            @keyframes bounce {
                0%, 20%, 50%, 80%, 100% {
                    transform: translateY(0);
                }
                40% {
                    transform: translateY(-10px);
                }
                60% {
                    transform: translateY(-5px);
                }
            }
            
            @keyframes fadeOut {
                from { opacity: 1; }
                to { opacity: 0; }
            }
        `;
        document.head.appendChild(styles);
    }
    
    document.body.appendChild(successModal);
    
    // Auto-cerrar después de 3 segundos
    setTimeout(() => {
        if (document.getElementById('modal-exito-resena')) {
            cerrarMensajeExitoResena();
        }
    }, 3000);
}

// Función para cerrar el mensaje de éxito de reseña
function cerrarMensajeExitoResena() {
    const modal = document.getElementById('modal-exito-resena');
    if (modal) {
        modal.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            modal.remove();
        }, 300);
    }
}
