import logging
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class DebugMiddleware(MiddlewareMixin):
    """
    Middleware para capturar errores antes de que lleguen a las vistas
    """
    
    def process_request(self, request):
        print(f"=== MIDDLEWARE REQUEST ===")
        print(f"URL: {request.path}")
        print(f"Método: {request.method}")
        print(f"Usuario: {request.user}")
        print(f"Headers: {dict(request.headers)}")
        
        # Específicamente para la URL de crear propiedad
        if request.path == '/propiedades/crear/' and request.method == 'POST':
            print(f"=== POST A CREAR PROPIEDAD ===")
            print(f"Datos POST: {dict(request.POST)}")
            print(f"Archivos: {list(request.FILES.keys())}")
            
        return None
    
    def process_response(self, request, response):
        print(f"=== MIDDLEWARE RESPONSE ===")
        print(f"Status: {response.status_code}")
        print(f"Content-Type: {response.get('Content-Type', 'N/A')}")
        
        return response
    
    def process_exception(self, request, exception):
        print(f"=== MIDDLEWARE EXCEPTION ===")
        print(f"URL: {request.path}")
        print(f"Excepción: {exception}")
        print(f"Tipo: {type(exception)}")
        print(f"Traceback: {traceback.format_exc()}")
        
        logger.error(f"Middleware capturó excepción: {exception}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        # Si es una petición AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error del middleware: {str(exception)}',
                'error_type': str(type(exception).__name__)
            })
        
        return None
