from django.db import models
from django.utils import timezone


class ContactSubmission(models.Model):
    """Modelo para almacenar envíos del formulario de contacto"""
    
    ASUNTO_CHOICES = [
        ('alquiler', 'Alquiler'),
    ]
    
    nombre = models.CharField(max_length=100, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    asunto = models.CharField(max_length=20, choices=ASUNTO_CHOICES, verbose_name="Asunto")
    mensaje = models.TextField(verbose_name="Mensaje")
    fecha_entrada = models.DateField(blank=True, null=True, verbose_name="Fecha de Entrada")
    fecha_salida = models.DateField(blank=True, null=True, verbose_name="Fecha de Salida")
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")
    
    class Meta:
        verbose_name = "Envío de Contacto"
        verbose_name_plural = "Envíos de Contacto"
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"{self.nombre} - {self.get_asunto_display()} ({self.fecha_envio.strftime('%d/%m/%Y')})"
    
    def get_asunto_display(self):
        """Retorna el display del asunto"""
        return dict(self.ASUNTO_CHOICES).get(self.asunto, self.asunto)


class CVSubmission(models.Model):
    """Modelo para almacenar CVs enviados por candidatos"""
    
    POSITION_CHOICES = [
        ('agente_inmobiliario', 'Agente Inmobiliario'),
        ('asesor_comercial', 'Asesor Comercial'),
        ('gerente_ventas', 'Gerente de Ventas'),
        ('administrativo', 'Personal Administrativo'),
        ('marketing', 'Especialista en Marketing'),
        ('contabilidad', 'Contabilidad'),
        ('legal', 'Asesoría Legal'),
        ('otro', 'Otra posición'),
    ]
    
    EXPERIENCE_CHOICES = [
        ('sin_experiencia', 'Sin experiencia'),
        ('1-2', '1-2 años'),
        ('3-5', '3-5 años'),
        ('6-10', '6-10 años'),
        ('10+', 'Más de 10 años'),
    ]
    
    EDUCATION_CHOICES = [
        ('secundario', 'Secundario Completo'),
        ('terciario', 'Terciario'),
        ('universitario', 'Universitario'),
        ('posgrado', 'Posgrado'),
    ]
    
    # Información personal
    nombre_completo = models.CharField(max_length=200, verbose_name="Nombre Completo")
    email = models.EmailField(verbose_name="Correo Electrónico")
    telefono = models.CharField(max_length=20, blank=True, null=True, verbose_name="Teléfono")
    
    # Información profesional
    posicion_interes = models.CharField(
        max_length=50, 
        choices=POSITION_CHOICES, 
        verbose_name="Posición de Interés"
    )
    anos_experiencia = models.CharField(
        max_length=20, 
        choices=EXPERIENCE_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Años de Experiencia"
    )
    nivel_educativo = models.CharField(
        max_length=20, 
        choices=EDUCATION_CHOICES, 
        blank=True, 
        null=True, 
        verbose_name="Nivel Educativo"
    )
    
    # Archivos
    cv_file = models.FileField(
        upload_to='cvs/%Y/%m/%d/', 
        verbose_name="Archivo CV",
        help_text="Formatos aceptados: PDF, DOC, DOCX"
    )
    carta_presentacion = models.TextField(
        blank=True, 
        null=True, 
        verbose_name="Carta de Presentación"
    )
    
    # Metadatos
    fecha_envio = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Envío")
    procesado = models.BooleanField(default=False, verbose_name="Procesado")
    notas_admin = models.TextField(blank=True, null=True, verbose_name="Notas del Administrador")
    
    class Meta:
        verbose_name = "CV Enviado"
        verbose_name_plural = "CVs Enviados"
        ordering = ['-fecha_envio']
    
    def __str__(self):
        return f"CV de {self.nombre_completo} - {self.get_posicion_interes_display()}"
    
    def get_file_size(self):
        """Retorna el tamaño del archivo en formato legible"""
        if self.cv_file:
            size = self.cv_file.size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return "N/A"
    
    def get_file_extension(self):
        """Retorna la extensión del archivo"""
        if self.cv_file:
            return self.cv_file.name.split('.')[-1].upper()
        return "N/A"
