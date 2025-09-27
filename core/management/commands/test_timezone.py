from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import datetime
import pytz

class Command(BaseCommand):
    help = 'Probar la configuración de zona horaria'

    def handle(self, *args, **options):
        self.stdout.write("🕐 Probando configuración de zona horaria...")
        self.stdout.write("-" * 50)
        
        # Hora actual en UTC
        utc_now = datetime.now(pytz.UTC)
        self.stdout.write(f"🌍 Hora UTC: {utc_now.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Hora actual en zona horaria configurada
        local_now = timezone.now()
        self.stdout.write(f"🇦🇷 Hora Argentina: {local_now.strftime('%d/%m/%Y %H:%M:%S')}")
        
        # Diferencia de horas
        diff_hours = (local_now.hour - utc_now.hour) % 24
        self.stdout.write(f"⏰ Diferencia: {diff_hours} horas")
        
        self.stdout.write("-" * 50)
        
        if diff_hours == 3:
            self.stdout.write(self.style.SUCCESS("✅ Zona horaria configurada correctamente (UTC-3)"))
        else:
            self.stdout.write(self.style.WARNING(f"⚠️  Diferencia inesperada: {diff_hours} horas"))
        
        self.stdout.write("\n📧 Ahora cuando envíes un formulario, la hora debería mostrar:")
        self.stdout.write(f"   {local_now.strftime('%d/%m/%Y %H:%M')} (hora de Argentina)")
