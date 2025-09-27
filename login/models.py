from django.db import models
from django.contrib.auth.models import User
import pyotp
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64

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
    
    # Campos para 2FA
    totp_secret = models.CharField(max_length=32, blank=True, null=True, verbose_name="Clave Secreta TOTP")
    two_factor_enabled = models.BooleanField(default=False, verbose_name="2FA Habilitado")
    backup_codes = models.JSONField(default=list, blank=True, verbose_name="Códigos de Respaldo")
    
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
    
    def generate_totp_secret(self):
        """Genera una nueva clave secreta TOTP"""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret
    
    def get_totp_uri(self):
        """Genera la URI TOTP para Google Authenticator"""
        if not self.totp_secret:
            self.generate_totp_secret()
            self.save()
        
        totp = pyotp.TOTP(self.totp_secret)
        return totp.provisioning_uri(
            name=self.email,
            issuer_name="Tienda Inmobiliaria"
        )
    
    def get_qr_code(self):
        """Genera el código QR para Google Authenticator"""
        uri = self.get_totp_uri()
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return base64.b64encode(buffer.getvalue()).decode()
    
    def verify_totp(self, token):
        """Verifica un código TOTP"""
        if not self.totp_secret:
            return False
        
        totp = pyotp.TOTP(self.totp_secret)
        return totp.verify(token, valid_window=1)
    
    def generate_backup_codes(self, count=10):
        """Genera códigos de respaldo"""
        import secrets
        import string
        
        codes = []
        for _ in range(count):
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))
            codes.append(code)
        
        self.backup_codes = codes
        return codes
    
    def verify_backup_code(self, code):
        """Verifica un código de respaldo"""
        if code in self.backup_codes:
            self.backup_codes.remove(code)
            self.save()
            return True
        return False
    
    def enable_2fa(self):
        """Habilita 2FA para el administrador"""
        if not self.totp_secret:
            self.generate_totp_secret()
        
        self.two_factor_enabled = True
        if not self.backup_codes:
            self.generate_backup_codes()
        
        self.save()
    
    def disable_2fa(self):
        """Deshabilita 2FA para el administrador"""
        self.two_factor_enabled = False
        self.totp_secret = None
        self.backup_codes = []
        self.save()


class PasswordResetCode(models.Model):
    """Modelo para códigos de recuperación de contraseña"""
    email = models.EmailField(verbose_name="Correo Electrónico")
    code = models.CharField(max_length=6, verbose_name="Código de Verificación")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Creación")
    used = models.BooleanField(default=False, verbose_name="Usado")
    expires_at = models.DateTimeField(verbose_name="Fecha de Expiración")
    
    class Meta:
        verbose_name = "Código de Recuperación"
        verbose_name_plural = "Códigos de Recuperación"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Código para {self.email} - {self.code}"
    
    def is_expired(self):
        """Verifica si el código ha expirado"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Verifica si el código es válido (no usado y no expirado)"""
        return not self.used and not self.is_expired()
    
    def mark_as_used(self):
        """Marca el código como usado"""
        self.used = True
        self.save()
    
    @classmethod
    def generate_code(cls, email):
        """Genera un nuevo código de recuperación"""
        import secrets
        import string
        from django.utils import timezone
        from django.conf import settings
        
        # Eliminar códigos anteriores para este email
        cls.objects.filter(email=email).delete()
        
        # Generar código de 6 dígitos
        code = ''.join(secrets.choice(string.digits) for _ in range(settings.PASSWORD_RESET_CODE_LENGTH))
        
        # Calcular fecha de expiración
        expires_at = timezone.now() + timezone.timedelta(seconds=settings.PASSWORD_RESET_TIMEOUT)
        
        # Crear nuevo código
        reset_code = cls.objects.create(
            email=email,
            code=code,
            expires_at=expires_at
        )
        
        return reset_code
