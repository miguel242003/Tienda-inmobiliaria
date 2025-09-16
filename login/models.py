from django.db import models
from django.contrib.auth.models import User

# Crea tus modelos aquí.

class AdminCredentials(models.Model):
    """Modelo para almacenar credenciales del administrador de forma segura"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='admincredentials', verbose_name="Usuario")
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Administrador", blank=True, null=True)
    apellido = models.CharField(max_length=100, verbose_name="Apellido del Administrador", blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name="Correo del Administrador")
    telefono = models.CharField(max_length=20, verbose_name="Teléfono del Administrador", blank=True, null=True)
    fecha_nacimiento = models.DateField(verbose_name="Fecha de Nacimiento", blank=True, null=True, help_text="Fecha de nacimiento del administrador (opcional)")
    foto_perfil = models.ImageField(
        upload_to='admin_profiles/',
        blank=True,
        null=True,
        verbose_name="Foto de Perfil",
        help_text="Foto de perfil del administrador (opcional)"
    )
    password = models.CharField(max_length=128, verbose_name="Contraseña (encriptada)")
    fecha_creacion = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    activo = models.BooleanField(default=True, verbose_name="Credenciales Activas")
    
    class Meta:
        verbose_name = "Credenciales de Administrador"
        verbose_name_plural = "Credenciales de Administrador"
    
    def __str__(self):
        if self.nombre and self.apellido:
            return f"Admin: {self.nombre} {self.apellido} ({self.email})"
        return f"Admin: {self.email}"
    
    def get_nombre_completo(self):
        """Retorna el nombre completo del administrador"""
        if self.nombre and self.apellido:
            return f"{self.nombre} {self.apellido}"
        return "Administrador del Sistema"
    
    def get_foto_perfil_url(self):
        """Retorna la URL de la foto de perfil o None si no existe"""
        if self.foto_perfil:
            try:
                # Verificar que el archivo existe físicamente
                if self.foto_perfil.storage.exists(self.foto_perfil.name):
                    return self.foto_perfil.url
                else:
                    print(f"Archivo no encontrado: {self.foto_perfil.name}")
                    return None
            except Exception as e:
                print(f"Error al obtener URL de foto: {e}")
                return None
        return None
    
    def save(self, *args, **kwargs):
        # Encriptar la contraseña antes de guardar
        if not self.pk:  # Solo si es nueva
            from django.contrib.auth.hashers import make_password
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
