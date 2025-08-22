from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class AdminCredentials(models.Model):
    """Modelo para almacenar credenciales del administrador de forma segura"""
    email = models.EmailField(unique=True, verbose_name="Correo del Administrador")
    password = models.CharField(max_length=128, verbose_name="Contraseña (encriptada)")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    activo = models.BooleanField(default=True, verbose_name="Credenciales Activas")
    
    class Meta:
        verbose_name = "Credenciales de Administrador"
        verbose_name_plural = "Credenciales de Administrador"
    
    def __str__(self):
        return f"Admin: {self.email}"
    
    def save(self, *args, **kwargs):
        # Encriptar la contraseña antes de guardar
        if not self.pk:  # Solo si es nueva
            from django.contrib.auth.hashers import make_password
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
