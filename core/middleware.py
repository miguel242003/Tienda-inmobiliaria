import logging
import traceback
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class DebugMiddleware(MiddlewareMixin):
    """
    Middleware simplificado para debug
    """
    
    def process_request(self, request):
        # Solo debug para crear propiedad
        if request.path == '/propiedades/crear/' and request.method == 'POST':
            print(f"=== MIDDLEWARE: POST A CREAR PROPIEDAD ===")
            print(f"URL: {request.path}")
            print(f"Usuario: {request.user}")
            print(f"Archivos: {list(request.FILES.keys())}")
            
        return None
    
    def process_exception(self, request, exception):
        print(f"=== MIDDLEWARE EXCEPTION ===")
        print(f"URL: {request.path}")
        print(f"Excepción: {exception}")
        print(f"Tipo: {type(exception)}")
        
        # Si es una petición AJAX, devolver JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'message': f'Error del middleware: {str(exception)}',
                'error_type': str(type(exception).__name__)
            })
        
        return None
