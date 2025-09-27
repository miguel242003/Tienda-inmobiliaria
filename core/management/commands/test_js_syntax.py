from django.core.management.base import BaseCommand
from django.test import Client
from propiedades.models import Propiedad
import re


class Command(BaseCommand):
    help = 'Verifica que no haya errores de sintaxis JavaScript en la página'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🧪 Verificando sintaxis JavaScript...'))
        
        # Obtener una propiedad de prueba
        try:
            propiedad = Propiedad.objects.first()
            if not propiedad:
                self.stdout.write(self.style.ERROR('❌ No hay propiedades en la base de datos'))
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error obteniendo propiedad: {e}'))
            return
        
        self.stdout.write(self.style.SUCCESS(f'📋 Usando propiedad: {propiedad.titulo}'))
        
        # Crear cliente de prueba
        client = Client()
        
        # Obtener la página de detalle
        try:
            response = client.get(f'/propiedades/{propiedad.id}/')
            
            if response.status_code == 200:
                self.stdout.write(self.style.SUCCESS('✅ Página de detalle cargada correctamente'))
                
                # Extraer el contenido JavaScript
                content = response.content.decode('utf-8')
                
                # Buscar el bloque de script
                script_match = re.search(r'<script>(.*?)</script>', content, re.DOTALL)
                if script_match:
                    js_content = script_match.group(1)
                    self.stdout.write(self.style.SUCCESS('✅ Bloque JavaScript encontrado'))
                    
                    # Verificar llaves balanceadas
                    open_braces = js_content.count('{')
                    close_braces = js_content.count('}')
                    
                    if open_braces == close_braces:
                        self.stdout.write(self.style.SUCCESS(f'✅ Llaves balanceadas: {open_braces} abiertas, {close_braces} cerradas'))
                    else:
                        self.stdout.write(self.style.ERROR(f'❌ Llaves desbalanceadas: {open_braces} abiertas, {close_braces} cerradas'))
                    
                    # Verificar paréntesis balanceados
                    open_parens = js_content.count('(')
                    close_parens = js_content.count(')')
                    
                    if open_parens == close_parens:
                        self.stdout.write(self.style.SUCCESS(f'✅ Paréntesis balanceados: {open_parens} abiertos, {close_parens} cerrados'))
                    else:
                        self.stdout.write(self.style.ERROR(f'❌ Paréntesis desbalanceados: {open_parens} abiertos, {close_parens} cerrados'))
                    
                    # Verificar comillas balanceadas
                    single_quotes = js_content.count("'")
                    double_quotes = js_content.count('"')
                    
                    if single_quotes % 2 == 0:
                        self.stdout.write(self.style.SUCCESS(f'✅ Comillas simples balanceadas: {single_quotes}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'❌ Comillas simples desbalanceadas: {single_quotes}'))
                    
                    if double_quotes % 2 == 0:
                        self.stdout.write(self.style.SUCCESS(f'✅ Comillas dobles balanceadas: {double_quotes}'))
                    else:
                        self.stdout.write(self.style.ERROR(f'❌ Comillas dobles desbalanceadas: {double_quotes}'))
                    
                    # Buscar posibles errores comunes
                    if '});' in js_content and js_content.count('});') > js_content.count('addEventListener'):
                        self.stdout.write(self.style.WARNING('⚠️ Posibles llaves extra después de addEventListener'))
                    
                    if 'function(' in js_content and 'function (' in js_content:
                        self.stdout.write(self.style.WARNING('⚠️ Inconsistencia en definición de funciones'))
                    
                else:
                    self.stdout.write(self.style.ERROR('❌ Bloque JavaScript no encontrado'))
                
            else:
                self.stdout.write(self.style.ERROR(f'❌ Error cargando página: {response.status_code}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error en la prueba: {e}'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Verificación de sintaxis JavaScript completada'))
